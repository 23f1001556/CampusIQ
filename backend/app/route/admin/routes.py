from flask import Blueprint, jsonify, request
from app.configs.extensions import db
from app.models.users import User
from app.models.subject import Subject
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.mock_quiz import MockQuiz, MockAttempt
from app.models.score import Scores
from app.auth.decors import login_required, admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/details", methods=["GET"])
@login_required
@admin_required
def get_dashboard_details():
    try:
        user_count = User.query.count()
        subject_count = Subject.query.count()
        quiz_count = Quiz.query.count() + MockQuiz.query.count()
        question_count = Question.query.count() # + MockQuestion count if needed, but this is a good start

        return jsonify({
            "user_count": user_count,
            "subject_count": subject_count,
            "quiz_count": quiz_count,
            "question_count": question_count
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@admin_bp.route("/attempts_stats", methods=["GET"])
@login_required
@admin_required
def get_attempts_stats():
    try:
        # Fetch recent attempts from both Standard and Mock quizzes
        # Limit to last 50 to render a readable chart
        
        # Standard Quizzes
        std_scores = (db.session.query(Scores, User.user_name, Quiz.name)
            .join(User, Scores.user_id == User.id)
            .join(Quiz, Scores.quiz_id == Quiz.id)
            .order_by(Scores.timestamp.desc())
            .limit(30)
            .all())

        # Mock Quizzes
        mock_attempts = (db.session.query(MockAttempt, User.user_name, MockQuiz.title)
            .join(User, MockAttempt.user_id == User.id)
            .join(MockQuiz, MockAttempt.mock_quiz_id == MockQuiz.id)
            .filter(MockAttempt.score.isnot(None)) # Only submitted attempts
            .order_by(MockAttempt.submitted_at.desc())
            .limit(30)
            .all())

        stats = []

        for score, username, quiz_name in std_scores:
            stats.append({
                "user": username,
                "quiz": quiz_name,
                "score": score.total_score,
                "date": score.timestamp.isoformat(),
                "type": "Standard"
            })

        for attempt, username, quiz_title in mock_attempts:
            stats.append({
                "user": username,
                "quiz": quiz_title,
                "score": attempt.score,
                "date": attempt.submitted_at.isoformat(),
                "type": "Mock"
            })

        # Sort combined list by date
        stats.sort(key=lambda x: x['date'], reverse=True)
        
        # Return top 30 combined
        return jsonify({"attempts": stats[:30]}), 200

    except Exception as e:
        print(e)
        return jsonify({"message": str(e)}), 500

@admin_bp.route("/user/<int:user_id>/scores", methods=["GET"])
@login_required
@admin_required
def get_user_scores(user_id):
    try:
        from app.models.score import Scores
        from app.models.mock_quiz import MockAttempt, MockQuiz
        from app.models.quiz import Quiz
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Standard Quizzes
        std_scores = (db.session.query(Scores, Quiz.name)
            .join(Quiz, Scores.quiz_id == Quiz.id)
            .filter(Scores.user_id == user_id)
            .order_by(Scores.timestamp.desc())
            .all())

        # Mock Quizzes
        mock_attempts = (db.session.query(MockAttempt, MockQuiz.title)
            .join(MockQuiz, MockAttempt.mock_quiz_id == MockQuiz.id)
            .filter(MockAttempt.user_id == user_id)
            .filter(MockAttempt.score.isnot(None))
            .order_by(MockAttempt.submitted_at.desc())
            .all())

        results = []
        for s, q_name in std_scores:
            results.append({
                "quiz": q_name,
                "score": s.total_score,
                "date": s.timestamp.isoformat(),
                "type": "Standard"
            })
        
        for m, q_title in mock_attempts:
            results.append({
                "quiz": q_title,
                "score": m.score,
                "date": m.submitted_at.isoformat(),
                "type": "Mock"
            })

        results.sort(key=lambda x: x['date'], reverse=True)

        return jsonify({
            "user": user.fullname or user.user_name,
            "scores": results
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
