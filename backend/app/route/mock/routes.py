from flask import Blueprint, jsonify, request
from app.auth.decors import login_required, admin_required, staff_required
from app.models.mock_quiz import MockQuiz, MockQuestion, MockAttempt
from app.configs.extensions import db
from datetime import datetime
import json

mock_bp = Blueprint("mock", __name__, url_prefix="/mock")

# --- ADMIN ENDPOINTS ---

@mock_bp.route("/create", methods=["POST"])
@login_required
@staff_required
def create_mock_quiz():
    try:
        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        start_time_str = data.get("start_time")
        end_time_str = data.get("end_time")
        duration_minutes = data.get("duration_minutes")

        if not all([title, start_time_str, end_time_str, duration_minutes]):
            return jsonify({"message": "Missing required fields"}), 400

        try:
             start_time = datetime.fromisoformat(start_time_str)
             end_time = datetime.fromisoformat(end_time_str)
        except ValueError:
             return jsonify({"message": "Invalid date format (ISO required)"}), 400

        mock_quiz = MockQuiz(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=int(duration_minutes),
            created_by=request.user_id,
            is_published=False
        )
        
        db.session.add(mock_quiz)
        db.session.commit()
        
        return jsonify({"message": "Mock Quiz created", "id": mock_quiz.id}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@mock_bp.route("/add_question", methods=["POST"])
@login_required
@staff_required
def add_mock_question():
    try:
        data = request.get_json()
        mock_quiz_id = data.get("mock_quiz_id")
        statement = data.get("statement")
        options = [data.get(f"option_{i}") for i in range(1, 5)]
        correct_option = data.get("correct_option") # "1", "2", "3", "4"
        marks = data.get("marks", 1)

        if not all([mock_quiz_id, statement, correct_option] + options):
             return jsonify({"message": "Missing required fields"}), 400

        mock_quiz = MockQuiz.query.get(mock_quiz_id)
        if not mock_quiz:
             return jsonify({"message": "Mock Quiz not found"}), 404

        question = MockQuestion(
            mock_quiz_id=mock_quiz_id,
            statement=statement,
            option_1=options[0],
            option_2=options[1],
            option_3=options[2],
            option_4=options[3],
            correct_option=str(correct_option),
            marks=marks
        )
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({"message": "Question added", "id": question.id}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@mock_bp.route("/publish/<int:id>", methods=["POST"])
@login_required
@staff_required
def publish_results(id):
    try:
        mock_quiz = MockQuiz.query.get(id)
        if not mock_quiz:
            return jsonify({"message": "Mock Quiz not found"}), 404
        
        mock_quiz.is_published = True
        db.session.commit()
        return jsonify({"message": "Results published"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# --- USER ENDPOINTS ---

@mock_bp.route("/list", methods=["GET"])
@login_required
def list_mock_quizzes():
    try:
        # Show all quizzes (active/upcoming/past) so users can see what's available
        quizzes = MockQuiz.query.order_by(MockQuiz.start_time.desc()).all()
        output = []
        for q in quizzes:
            # Check if user attempted - get LATEST
            attempt = MockAttempt.query.filter_by(mock_quiz_id=q.id, user_id=request.user_id)\
                .order_by(MockAttempt.submitted_at.desc()).first()
            
            # Calculate total marks for the quiz
            total_marks = 0
            for question in q.questions:
                total_marks += question.marks

            output.append({
                "id": q.id,
                "title": q.title,
                "start_time": q.start_time.isoformat(),
                "end_time": q.end_time.isoformat(),
                "duration_minutes": q.duration_minutes,
                "is_active": q.start_time <= datetime.utcnow() <= q.end_time,
                "attempted": bool(attempt),
                "score": attempt.score if attempt else None,
                "total_marks": total_marks,
                "is_published": q.is_published,
                "is_submitted": attempt.score is not None if attempt else False
            })
        return jsonify({"quizzes": output}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@mock_bp.route("/start", methods=["POST"])
@login_required
def start_mock_attempt():
    try:
        data = request.get_json()
        mock_quiz_id = data.get("mock_quiz_id")
        
        if not mock_quiz_id:
             return jsonify({"message": "Missing mock_quiz_id"}), 400

        mock_quiz = MockQuiz.query.get(mock_quiz_id)
        if not mock_quiz:
             return jsonify({"message": "Mock Quiz not found"}), 404

        # Check existing attempt
        existing_attempt = MockAttempt.query.filter_by(mock_quiz_id=mock_quiz_id, user_id=request.user_id).first()
        if existing_attempt:
            # If submitted (score not None), prevent re-entry
            if existing_attempt.score is not None:
                 return jsonify({"message": "You have already attempted this quiz."}), 403
            # If not submitted, return success (resume or just ok)
            return jsonify({"message": "Quiz started", "attempt_id": existing_attempt.id}), 200

        # Create new attempt (Started state)
        attempt = MockAttempt(
            user_id=request.user_id,
            mock_quiz_id=mock_quiz_id,
            score=None,
            _answers=None,
            started_at=datetime.utcnow()
        )
        
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({"message": "Quiz started", "attempt_id": attempt.id}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@mock_bp.route("/attempt", methods=["POST"])
@login_required
def attempt_mock_quiz():
    try:
        data = request.get_json()
        mock_quiz_id = data.get("mock_quiz_id")
        answers = data.get("answers") # {"q_id": "option"}

        if not mock_quiz_id or not answers:
             return jsonify({"message": "Missing quiz_id or answers"}), 400

        mock_quiz = MockQuiz.query.get(mock_quiz_id)
        if not mock_quiz:
             return jsonify({"message": "Mock Quiz not found"}), 404

        # Validate Time (Optional strict check)
        now = datetime.utcnow()
        # We allow submission even if slightly past end_time due to latency, 
        # but logic can be stricter if needed.

        # Find the STARTED attempt
        attempt = MockAttempt.query.filter_by(mock_quiz_id=mock_quiz_id, user_id=request.user_id).first()
        
        if not attempt:
             return jsonify({"message": "No active attempt found. Please start the quiz first."}), 400
        
        if attempt.score is not None:
             return jsonify({"message": "Quiz already submitted."}), 403

        # Calculate Score
        score = 0
        questions = MockQuestion.query.filter_by(mock_quiz_id=mock_quiz_id).all()
        question_map = {str(q.id): q for q in questions}

        for q_id, selected_opt in answers.items():
            if q_id in question_map:
                if str(selected_opt) == question_map[q_id].correct_option:
                    score += question_map[q_id].marks

        # Update Attempt
        attempt.score = score
        attempt.answers = answers # Property handles json dumping
        attempt.submitted_at = now
        
        db.session.commit()
        
        return jsonify({"message": "Attempt submitted", "score": score}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@mock_bp.route("/quiz/<int:id>", methods=["GET"])
@login_required
def get_mock_quiz_for_attempt(id):
    try:
        mock_quiz = MockQuiz.query.get(id)
        if not mock_quiz:
             return jsonify({"message": "Mock Quiz not found"}), 404

        # Validate Time
        now = datetime.utcnow()
        if now < mock_quiz.start_time:
             return jsonify({"message": "Quiz has not started yet"}), 400
        if now > mock_quiz.end_time:
             pass 

        questions = MockQuestion.query.filter_by(mock_quiz_id=id).all()
        q_list = []
        for q in questions:
            q_list.append({
                "id": q.id,
                "statement": q.statement,
                "option_1": q.option_1,
                "option_2": q.option_2,
                "option_3": q.option_3,
                "option_4": q.option_4,
                "marks": q.marks
            })

        return jsonify({
            "id": mock_quiz.id,
            "title": mock_quiz.title,
            "description": mock_quiz.description,
            "duration_minutes": mock_quiz.duration_minutes,
            "end_time": mock_quiz.end_time.isoformat(),
            "questions": q_list
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@mock_bp.route("/get_result/<int:attempt_id>", methods=["GET"])
@login_required
def get_mock_result(attempt_id):
    try:
        # Get attempt by ID
        attempt = MockAttempt.query.get(attempt_id)
        if not attempt:
            return jsonify({"message": "Result not found"}), 404

        # Access check: Owner OR Admin
        is_admin = getattr(request, "isadmin", False)
        if attempt.user_id != request.user_id and not is_admin:
            return jsonify({"message": "Access denied"}), 403

        mock_quiz = MockQuiz.query.get(attempt.mock_quiz_id)
        
        # Build detailed result
        questions = MockQuestion.query.filter_by(mock_quiz_id=mock_quiz_id).all()
        user_answers = attempt.answers
        
        details = []
        for q in questions:
            user_ans = user_answers.get(str(q.id))
            details.append({
                "statement": q.statement,
                "options": {
                    "1": q.option_1, "2": q.option_2, "3": q.option_3, "4": q.option_4
                },
                "correct_option": q.correct_option,
                "user_selected": user_ans,
                "is_correct": user_ans == q.correct_option
            })

        return jsonify({
            "score": attempt.score,
            "total_questions": len(questions),
            "details": details,
            "is_published": mock_quiz.is_published
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@mock_bp.route("/leaderboard/<int:mock_quiz_id>", methods=["GET"])
@login_required
def get_leaderboard(mock_quiz_id):
    try:
        mock_quiz = MockQuiz.query.get(mock_quiz_id)
        if not mock_quiz:
             return jsonify({"message": "Quiz not found"}), 404

        if not mock_quiz.is_published:
             # Regular users can't see unless published
             if not getattr(request, "isadmin", False):
                  return jsonify({"message": "Results not published yet"}), 403

        # Fetch top attempts
        attempts = MockAttempt.query.filter_by(mock_quiz_id=mock_quiz_id)\
            .order_by(MockAttempt.score.desc(), MockAttempt.submitted_at.asc())\
            .all()

        leaderboard = []
        rank = 1
        for att in attempts:
            leaderboard.append({
                "rank": rank,
                "user_name": att.user.user_name,
                "fullname": att.user.fullname,
                "score": att.score,
                "submitted_at": att.submitted_at.isoformat()
            })
            rank += 1
            
        return jsonify({"leaderboard": leaderboard}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
