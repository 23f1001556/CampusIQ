from flask import Blueprint, jsonify, request
from app.auth.decors import login_required
from app.models.quiz import Quiz
from app.models.chapter import Chapter
from app.models.subject import Subject
from app.celery.tasks import notify_new_quiz
from app.configs.extensions import db
from datetime import datetime

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")

@quiz_bp.route("/createquiz", methods=["POST"])
@login_required
def create_quiz():
    try:
        data = request.get_json()
        name = data.get("name")
        chapter_id = data.get("chapter_id")
        date_of_quiz_str = data.get("date_of_quiz")
        time_duration = data.get("time_duration")
        remarks = data.get("remarks")

        if not name or not chapter_id:
            return jsonify({"message": "Name and Chapter ID are required"}), 400
            
        # Verify Chapter ownership
        chapter = Chapter.query.join(Subject).filter(Chapter.id == chapter_id, Subject.user_id == request.user_id).first()
        if not chapter:
             return jsonify({"message": "Chapter not found or access denied"}), 404

        if time_duration:
            try:
                time_duration = int(time_duration)
            except ValueError:
                return jsonify({"message": "Time duration must be an integer (minutes)"}), 400

        date_of_quiz = datetime.utcnow()
        if date_of_quiz_str:
            try:
                # expecting format like '2023-01-01 12:00:00' or ISO
                date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Try ISO format if first fails, or just default to now/error
                try:
                    date_of_quiz = datetime.fromisoformat(date_of_quiz_str)
                except ValueError:
                     return jsonify({"message": "Invalid date format. Use YYYY-MM-DD HH:MM:SS"}), 400

        new_quiz = Quiz(
            name=name,
            chapter_id=chapter_id,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            remarks=remarks
        )

        db.session.add(new_quiz)
        db.session.commit()
        
        # Notify users
        if chapter and chapter.subject_id:
            subject = Subject.query.get(chapter.subject_id)
            if subject:
                notify_new_quiz.delay(name, subject.name)
        
        return jsonify({"message": "Quiz created successfully", "quiz_id": new_quiz.id}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@quiz_bp.route("/updatequiz/<int:id>", methods=["PUT"])
@login_required
def update_quiz(id):
    try:
        quiz = Quiz.query.join(Chapter).join(Subject).filter(Quiz.id == id, Subject.user_id == request.user_id).first()
        if not quiz:
            return jsonify({"message": "Quiz not found or access denied"}), 404

        data = request.get_json()

        if "name" in data:
            quiz.name = data["name"]
        if "chapter_id" in data:
             # Verify new chapter ownership
             new_chapter_id = data["chapter_id"]
             new_chapter = Chapter.query.join(Subject).filter(Chapter.id == new_chapter_id, Subject.user_id == request.user_id).first()
             if not new_chapter:
                  return jsonify({"message": "New Chapter not found or access denied"}), 404
             quiz.chapter_id = new_chapter_id
        
        if "time_duration" in data:
            try:
                quiz.time_duration = int(data["time_duration"])
            except ValueError:
                return jsonify({"message": "Time duration must be an integer (minutes)"}), 400
        if "remarks" in data:
            quiz.remarks = data["remarks"]
        if "date_of_quiz" in data:
             try:
                quiz.date_of_quiz = datetime.strptime(data["date_of_quiz"], '%Y-%m-%d %H:%M:%S')
             except ValueError:
                 try:
                     quiz.date_of_quiz = datetime.fromisoformat(data["date_of_quiz"])
                 except ValueError:
                     return jsonify({"message": "Invalid date format"}), 400

        db.session.commit()
        return jsonify({"message": "Quiz updated successfully"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@quiz_bp.route("/getquizzes", methods=["GET"])
@login_required
def get_quizzes():
    try:
        chapter_id = request.args.get("chapter_id")
        
        query = Quiz.query.join(Chapter).join(Subject).filter(Subject.user_id == request.user_id)
        
        # Pre-fetch scores for this user to avoid N+1 if possible, but for simplicity we can query inside loop or use a join
        # For now, let's keep it simple as list pagination isn't huge
        from app.models.score import Scores

        
        if chapter_id:
            query = query.filter(Quiz.chapter_id == chapter_id)
            
        quizzes = query.all()
        
        # Optimize: Fetch all attempt counts for these quizzes for this user at once
        # Group by quiz_id
        quiz_ids = [q.id for q in quizzes]
        attempt_map = {}
        if quiz_ids:
            # We need to count attempts per quiz for this user.
            # SQL: SELECT quiz_id, COUNT(*) FROM scores WHERE user_id = ? AND quiz_id IN (...) GROUP BY quiz_id
            from sqlalchemy import func
            attempts_query = db.session.query(Scores.quiz_id, func.count(Scores.id))\
                .filter(Scores.user_id == request.user_id, Scores.quiz_id.in_(quiz_ids))\
                .group_by(Scores.quiz_id).all()
            
            attempt_map = {quiz_id: count for quiz_id, count in attempts_query}

        output = []
        for quiz in quizzes:
            # Fetch Chapter Name
            chapter_name = quiz.chapter.name if quiz.chapter else "Unknown"
            
            output.append({
                "id": quiz.id,
                "name": quiz.name,
                "chapter_id": quiz.chapter_id,
                "chapter_name": chapter_name,
                "subject_id": quiz.chapter.subject_id if quiz.chapter else None,
                "date_of_quiz": quiz.date_of_quiz.strftime('%Y-%m-%d %H:%M:%S') if quiz.date_of_quiz else None,
                "time_duration": quiz.time_duration,
                "remarks": quiz.remarks,
                "is_published": quiz.is_published,
                "scores_released": quiz.scores_released,
                "question_count": len(quiz.questions),
                "attempt_count": attempt_map.get(quiz.id, 0)
            })
        return jsonify({"quizzes": output}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@quiz_bp.route("/getquiz/<int:id>", methods=["GET"])
@login_required
def get_quiz(id):
    try:
        # Check ownership OR published status
        quiz = Quiz.query.get(id)
        if not quiz:
             return jsonify({"message": "Quiz not found"}), 404

        # Access Logic:
        # 1. Owner can always view
        # 2. Admin (any admin?) - let's stick to owner for now, or published
        # 3. Public if published and within time
        
        is_owner = False
        if quiz.chapter and quiz.chapter.subject and quiz.chapter.subject.user_id == request.user_id:
            is_owner = True
            
        if not is_owner:
            # Must be published and time valid
            if not quiz.is_published:
                return jsonify({"message": "Access denied"}), 403
            
            # If strictly admin tool for other users? No, user said "visible to other Iusers"
            # Time check for non-owners
            now = datetime.utcnow()
            if quiz.start_time and now < quiz.start_time:
                 if not getattr(request, "isadmin", False): # Admin might preview?
                    return jsonify({"message": f"Quiz starts at {quiz.start_time}"}), 403
            if quiz.end_time and now > quiz.end_time: # Only enforce end time for attempt?
                 pass 
                 
            # Check re-attempts for Global Quiz
            if quiz.is_published: # It is a global quiz
                 from app.models.score import Scores
                 existing_attempt = Scores.query.filter_by(user_id=request.user_id, quiz_id=quiz.id).first()
                 if existing_attempt:
                      return jsonify({"message": "You have already attempted this quiz"}), 403

        # Fetch questions
        from app.models.question import Question

        # Fetch questions
        from app.models.question import Question
        questions = Question.query.filter_by(quiz_id=id).all()
        q_list = []
        for q in questions:
            q_list.append({
                "id": q.id,
                "statement": q.question_statement,
                "option_1": q.option_1,
                "option_2": q.option_2,
                "option_3": q.option_3,
                "option_4": q.option_4,
                "correct_option": q.correct_option # potentially hide this if pure attempt, but for now ok
            })

        quiz_data = {
            "id": quiz.id,
            "name": quiz.name,
            "chapter_id": quiz.chapter_id,
            "date_of_quiz": quiz.date_of_quiz.strftime('%Y-%m-%d %H:%M:%S') if quiz.date_of_quiz else None,
            "time_duration": quiz.time_duration,
            "remarks": quiz.remarks,
            "questions": q_list
        }
        return jsonify({"quiz": quiz_data}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@quiz_bp.route("/submit", methods=["POST"])
@login_required
def submit_quiz():
    try:
        data = request.get_json()
        quiz_id = data.get("quiz_id")
        answers = data.get("answers") # Dict {question_id: selected_option_str}

        if not quiz_id or not answers:
            return jsonify({"message": "Quiz ID and Answers are required"}), 400

        # Verify Quiz
        # Allow if User is Owner OR Quiz is Published
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({"message": "Quiz not found"}), 404
            
        # Check permissions
        is_owner = False
        if quiz.chapter and quiz.chapter.subject and quiz.chapter.subject.user_id == request.user_id:
            is_owner = True
            
        if not is_owner and not quiz.is_published:
             return jsonify({"message": "Access denied"}), 403

        from app.models.question import Question
        from app.models.score import Scores
        from app.models.user_response import UserResponse
        
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        total_questions = len(questions)
        score = 0
        
        results = []
        user_responses_to_save = [] # Prepare for DB
        
        for q in questions:
            user_ans = str(answers.get(str(q.id))) # Ensure string
            is_correct = (user_ans == q.correct_option)
            if is_correct:
                score += 1
            
            results.append({
                "question_id": q.id,
                "correct": is_correct,
                "user_answer": user_ans,
                "correct_answer": q.correct_option
            })
            
            # Prepare persistence
            user_responses_to_save.append({
                "question_id": q.id,
                "selected_option": user_ans
            })

        # Save Score
        new_score = Scores(
            user_id=request.user_id,
            quiz_id=quiz_id,
            total_score=score
        )
        db.session.add(new_score)
        db.session.flush() # flush to get ID
        
        # Save Responses
        for resp in user_responses_to_save:
            ur = UserResponse(
                score_id=new_score.id,
                question_id=resp["question_id"],
                selected_option=resp["selected_option"]
            )
            db.session.add(ur)
            
        db.session.commit()

        # Check release status
        show_score = True
        if quiz.is_published and not quiz.scores_released:
            show_score = False

        return jsonify({
            "score": score if show_score else None,
            "total": total_questions,
            "results": results if show_score else [],
            "score_id": new_score.id,
            "message": "Submission Successful. Waiting for results." if not show_score else "Submission Successful"
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@quiz_bp.route("/deletequiz/<int:id>", methods=["DELETE"])
@login_required
def delete_quiz(id):
    try:
        quiz = Quiz.query.join(Chapter).join(Subject).filter(Quiz.id == id, Subject.user_id == request.user_id).first()
        if not quiz:
            return jsonify({"message": "Quiz not found or access denied"}), 404
            
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({"message": "Quiz deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@quiz_bp.route("/get_result/<int:score_id>", methods=["GET"])
@login_required
def get_quiz_result(score_id):
    try:
        from app.models.score import Scores
        from app.models.question import Question
        from app.models.user_response import UserResponse
        
        score_record = Scores.query.get(score_id)
        if not score_record:
            return jsonify({"message": "Result not found"}), 404

        # Check access: Owner OR Admin
        is_admin = getattr(request, "isadmin", False)
        if score_record.user_id != request.user_id and not is_admin:
            return jsonify({"message": "Access denied"}), 403

        quiz = Quiz.query.get(score_record.quiz_id)
        if not quiz:
             return jsonify({"message": "Quiz not found"}), 404

        if quiz.is_published and not quiz.scores_released:
             # Check if admin?
             if not getattr(request, "isadmin", False):
                return jsonify({"message": "Results pending release"}), 403

        questions = Question.query.filter_by(quiz_id=quiz.id).all()
        
        # Fetch User Responses
        responses = UserResponse.query.filter_by(score_id=score_id).all()
        response_map = {r.question_id: r.selected_option for r in responses}
        
        q_details = []
        for q in questions:
            q_details.append({
                "id": q.id,
                "statement": q.question_statement,
                "options": {
                    "1": q.option_1,
                    "2": q.option_2,
                    "3": q.option_3,
                    "4": q.option_4
                },
                "correct_option": q.correct_option,
                "user_selected": response_map.get(q.id)
            })

        return jsonify({
            "score": score_record.total_score,
            "total_questions": len(questions),
            "quiz_name": quiz.name,
            "questions": q_details
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@quiz_bp.route("/save_generated", methods=["POST"])
@login_required
def save_generated_quiz():
    try:
        data = request.get_json()
        name = data.get("name")
        chapter_id = data.get("chapter_id")
        questions_data = data.get("questions") # List of dicts

        if not name or not chapter_id or not questions_data:
            return jsonify({"message": "Name, Chapter ID and Questions are required"}), 400

        # Verify Chapter
        chapter = Chapter.query.join(Subject).filter(Chapter.id == chapter_id, Subject.user_id == request.user_id).first()
        if not chapter:
             return jsonify({"message": "Chapter not found or access denied"}), 404

        # Create Quiz
        # Default duration 2 mins per question
        length = len(questions_data)
        new_quiz = Quiz(
            name=name,
            chapter_id=chapter_id,
            time_duration=length * 2, 
            remarks="AI Generated"
        )
        db.session.add(new_quiz)
        db.session.flush()

        # Create Questions
        from app.models.question import Question # Import here
        
        for q_data in questions_data:
            # Flexible Options Parsing
            options = q_data.get("options", {})
            opts = ["", "", "", ""]
            
            # Helper to find option text regardless of key format (A, a, 1, Option A, etc)
            def get_opt_text(keys):
                for k in keys:
                    if k in options: return options[k]
                    if k.lower() in options: return options[k.lower()]
                return ""

            opts[0] = get_opt_text(["A", "1", "Option A", "a"])
            opts[1] = get_opt_text(["B", "2", "Option B", "b"])
            opts[2] = get_opt_text(["C", "3", "Option C", "c"])
            opts[3] = get_opt_text(["D", "4", "Option D", "d"])

            # Flexible Answer Parsing
            raw_ans = str(q_data.get("answer", "A")).strip().upper()
            
            # Clean common prefixes like "Answer: A" or "Option A"
            import re
            match = re.search(r'([A-D])', raw_ans)
            if match:
                clean_ans = match.group(1)
            else:
                clean_ans = "A" # Default fallback
            
            ans_map = {"A": "1", "B": "2", "C": "3", "D": "4"}
            correct_opt = ans_map.get(clean_ans, "1")

            new_q = Question(
                quiz_id=new_quiz.id,
                chapter_id=chapter_id,
                question_statement=q_data.get("question", ""),
                option_1=opts[0],
                option_2=opts[1],
                option_3=opts[2],
                option_4=opts[3],
                correct_option=correct_opt,
                question_type="single"
            )
            db.session.add(new_q)

        db.session.commit()
        return jsonify({"message": "Quiz saved successfully", "quiz_id": new_quiz.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
@quiz_bp.route("/publish_quiz/<int:id>", methods=["POST"])
@login_required
def publish_quiz(id):
    try:
        # Only admin should publish? Or user who created it? 
        # User said "if user is admin then we will have option"
        if not getattr(request, "isadmin", False):
             return jsonify({"message": "Admin access required"}), 403

        quiz = Quiz.query.get(id)
        if not quiz:
            return jsonify({"message": "Quiz not found"}), 404

        data = request.get_json()

        start_time_str = data.get("start_time") # ISO
        end_time_str = data.get("end_time") # ISO

        if "is_published" in data:

            quiz.is_published = data["is_published"]
            
        if start_time_str and end_time_str:
            try:
                 quiz.start_time = datetime.fromisoformat(start_time_str)
                 quiz.end_time = datetime.fromisoformat(end_time_str)
                 quiz.is_published = True # Auto publish if times provided
            except ValueError:
                 return jsonify({"message": "Invalid date format"}), 400

        db.session.commit()
        return jsonify({"message": "Quiz updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@quiz_bp.route("/release_results/<int:id>", methods=["POST"])
@login_required
def release_results(id):
    try:
        if not getattr(request, "isadmin", False):
             return jsonify({"message": "Admin access required"}), 403

        quiz = Quiz.query.get(id)
        if not quiz:
            return jsonify({"message": "Quiz not found"}), 404


        quiz.scores_released = True
        db.session.commit()

        return jsonify({"message": "Results released successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@quiz_bp.route("/get_mock_quizzes", methods=["GET"])
@login_required
def get_mock_quizzes():
    try:
        from app.models.score import Scores
        
        # Fetch PUBLISHED quizzes
        # If user is admin, fetch all? No, just published ones for the mock list.
        # But wait, unpublishing should hide it.
        quizzes = Quiz.query.filter_by(is_published=True).order_by(Quiz.start_time.asc()).all()
        
        output = []
        now = datetime.utcnow()
        
        for q in quizzes:
            status = "upcoming"
            if now > q.end_time:
                status = "ended"
            elif now >= q.start_time and now <= q.end_time:
                status = "live"
                
            # Check for latest attempt
            score_record = Scores.query.filter_by(user_id=request.user_id, quiz_id=q.id)\
                .order_by(Scores.id.desc()).first()
                
            output.append({
                "id": q.id,
                "name": q.name,
                "start_time": q.start_time.isoformat() if q.start_time else None,
                "end_time": q.end_time.isoformat() if q.end_time else None,
                "time_duration": q.time_duration,
                "remarks": q.remarks,
                "status": status,
                "question_count": len(q.questions),
                "attempted": bool(score_record),
                "attempted": bool(score_record),
                "scores_released": q.scores_released,
                "score_id": score_record.id if score_record else None,
                "score": score_record.total_score if (score_record and q.scores_released) else None,
                # "total_marks": len(q.questions) # Assuming 1 mark per question for regular quizzes
                 "total_marks": len(q.questions) 
            })
            
        return jsonify({"quizzes": output}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@quiz_bp.route("/leaderboard", methods=["GET"])
@login_required
def get_leaderboard():
    try:
        from app.models.score import Scores
        from app.models.users import User
        from sqlalchemy import func, desc

        # 1. Aggrating Total Scores
        # Subquery to get total score per user
        subquery = db.session.query(
            Scores.user_id,
            func.sum(Scores.total_score).label('total_score')
        ).group_by(Scores.user_id).subquery()

        # Join with Users to get names
        query = db.session.query(
            User.user_name,
            subquery.c.total_score
        ).join(subquery, User.id == subquery.c.user_id)\
         .order_by(desc(subquery.c.total_score))

        all_scores = query.all() # [(username, score), ...]

        # 2. Process Stats
        leaderboard = []
        user_rank = -1
        user_score = 0
        current_user_name = ""
        
        # Determine Current User
        current_user = User.query.get(request.user_id)
        if current_user:
            current_user_name = current_user.user_name

        # Calculate Rank and Build List
        for rank, (name, score) in enumerate(all_scores, 1):
            leaderboard.append({
                "rank": rank,
                "username": name,
                "score": score
            })
            if name == current_user_name:
                user_rank = rank
                user_score = score

        # 3. Distribution Data (Histogram) for Graph
        scores_list = [s[1] for s in all_scores]
        distribution = {}
        
        if scores_list:
            max_s = max(scores_list) or 10
            # Create ~10-20 buckets
            bucket_size = max(5, int(max_s / 20) + 1) # Ensure at least size 5
            
            for s in scores_list:
                bucket_index = (s // bucket_size) * bucket_size
                label = f"{bucket_index}-{bucket_index + bucket_size}"
                distribution[label] = distribution.get(label, 0) + 1

        # Sort distribution by bucket index
        def get_start(k):
             return int(k.split('-')[0])
             
        sorted_keys = sorted(distribution.keys(), key=get_start)
        sorted_dist_labels = sorted_keys
        sorted_dist_values = [distribution[k] for k in sorted_keys]

        return jsonify({
            "leaderboard": leaderboard[:50], # Top 50
            "user_rank": user_rank,
            "user_score": user_score,
            "total_participants": len(all_scores),
            "graph_labels": sorted_dist_labels,
            "graph_values": sorted_dist_values
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500
