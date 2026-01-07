from flask import Blueprint, jsonify, request
from app.auth.decors import login_required
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Scores
from app.models.users import User
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.configs.extensions import db
from app.route.test_paper.analyzer import calculate_score
from flask_jwt_extended import get_jwt_identity
from app.celery.tasks import notify_marks_released

test_paper_bp = Blueprint("test_paper", __name__, url_prefix="/test_paper")

@test_paper_bp.route("/add_question", methods=["POST"])
@login_required 
def add_question():
    try:
        data = request.get_json()
        quiz_id = data.get("quiz_id")
        chapter_id = data.get("chapter_id")
        question_statement = data.get("question_statement")
        option_1 = data.get("option_1")
        option_2 = data.get("option_2")
        option_3 = data.get("option_3")
        option_4 = data.get("option_4")
        correct_option = data.get("correct_option") # Now Expecting String e.g. "1" or "1,2"
        question_type = data.get("question_type", "single") # Default to single

        # Basic Validation
        if not all([quiz_id, chapter_id, question_statement, option_1, option_2, option_3, option_4, correct_option]):
            return jsonify({"message": "Missing required fields"}), 400

        # Validate Quiz Existence
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({"message": "Quiz not found"}), 404
        
        # Validate question_type
        if question_type not in ["single", "multi"]:
             return jsonify({"message": "Invalid question_type. Must be 'single' or 'multi'"}), 400

        new_question = Question(
            quiz_id=quiz_id,
            chapter_id=chapter_id,
            question_statement=question_statement,
            option_1=option_1,
            option_2=option_2,
            option_3=option_3,
            option_4=option_4,
            correct_option=str(correct_option), # Ensure it's stored as string
            question_type=question_type
        )

        db.session.add(new_question)
        db.session.commit()

        return jsonify({
            "message": "Question added successfully",
            "question": {
                "id": new_question.id,
                "statement": new_question.question_statement,
                "type": new_question.question_type,
                "correct_option": new_question.correct_option
            }
        }), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@test_paper_bp.route("/submit", methods=["POST"])
@login_required
def submit_test():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        quiz_id = data.get("quiz_id")
        user_answers = data.get("answers") # Dict: {"1": "2", "2": "1,3"}

        if not quiz_id or not user_answers:
             return jsonify({"message": "Quiz ID and answers are required"}), 400

        # Calculate Score
        analysis = calculate_score(quiz_id, user_answers)
        
        # Save Score
        new_score = Scores(
            user_id=current_user_id['id'] if isinstance(current_user_id, dict) else current_user_id, # Handle if identity is object or int
            quiz_id=quiz_id,
            total_score=analysis["total_score"]
        )
        db.session.add(new_score)
        db.session.commit()

        # Notify user (Fetch email first)
        user = User.query.get(new_score.user_id)
        # Use Quiz object to get title
        quiz_obj = Quiz.query.get(quiz_id)
        if user and user.email and quiz_obj:
            notify_marks_released.delay(user.email, quiz_obj.name, analysis["total_score"])

        return jsonify({
            "message": "Test submitted successfully",
            "score_id": new_score.id,
            "analysis": analysis
        }), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@test_paper_bp.route("/history", methods=["GET"])
@login_required
def get_user_history():
    try:
        current_user_id = get_jwt_identity()
        user_id = current_user_id['id'] if isinstance(current_user_id, dict) else current_user_id
        
        # Join User -> Score -> Quiz -> Chapter -> Subject
        # But Scores has direct relation to Quiz. Quiz has Chapter. Chapter has Subject.
        
        scores = Scores.query.filter_by(user_id=user_id).order_by(Scores.timestamp.desc()).all()
        
        history = []
        for score in scores:
            quiz = score.quiz_id # Accessing related object might need proper backref setup or query
            # Assuming basic relations exist. If lazy loading issue, might need explicit join.
            # Using specific query logic to be safe:
            quiz_obj = Quiz.query.get(score.quiz_id)
            chapter_obj = Chapter.query.get(quiz_obj.chapter_id) if quiz_obj else None
            subject_obj = Subject.query.get(chapter_obj.subject_id) if chapter_obj else None
            
            history.append({
                "score_id": score.id,
                "score": score.total_score,
                "date": score.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "quiz_name": quiz_obj.name if quiz_obj else "Unknown",
                "chapter_name": chapter_obj.name if chapter_obj else "Unknown",
                "subject_name": subject_obj.name if subject_obj else "Unknown"
            })

        return jsonify({"history": history}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500
