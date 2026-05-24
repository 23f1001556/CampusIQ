from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
from app.models.users import User
from app.models.activity import ActivityLog
from app.configs.extensions import db
from app.auth.decors import protect_super_admin, login_required, admin_required, staff_required

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.route("/", methods=["GET"])
@users_bp.route("", methods=["GET"])
def users_index():
    return jsonify({"message": "Users API endpoint"}), 200

@users_bp.route("/getusers", methods=["GET"])
@login_required
@staff_required
def get_users():
    try:
        if request.role == 'manager':
            # Managers only see students in their domain
            domain = request.user.email_domain
            users = User.query.filter(User.email.like(f"%@{domain}"), User.role == 'user').all()
        else:
            # Admins see everyone
            users = User.query.all()
        output = []
        for user in users:
            output.append({
                "id": user.id,
                "user_name": user.user_name,
                "email": user.email,
                "fullname": user.fullname,
                "qualification": user.qualification,
                "dob": user.dob.strftime('%Y-%m-%d') if user.dob else None,
                "isadmin": user.isadmin,
                "role": user.role,
                "is_blocked": user.is_blocked if hasattr(user, 'is_blocked') else False
            })
        return jsonify({"users": output}), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": "Error fetching users"}), 500

@users_bp.route("/getuser/<int:id>", methods=["GET"])
@login_required
@protect_super_admin
def get_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        user_data = {
            "id": user.id,
            "user_name": user.user_name,
            "email": user.email,
            "fullname": user.fullname,
            "qualification": user.qualification,
            "dob": user.dob.strftime('%Y-%m-%d') if user.dob else None,
            "isadmin": user.isadmin,
            "role": user.role,
            "is_blocked": user.is_blocked if hasattr(user, 'is_blocked') else False
        }
        return jsonify({"user": user_data}), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": "Error fetching user details"}), 500

@users_bp.route("/updateuser/<int:id>", methods=["PUT"])
@login_required
@staff_required
@protect_super_admin
def update_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        if request.role == 'manager':
            if user.email_domain != request.user.email_domain:
                return jsonify({"message": "Access denied: User outside your domain"}), 403
            if user.role != 'user':
                return jsonify({"message": "Managers can only update standard users"}), 403
            
        data = request.get_json()
        
        if "fullname" in data:
            user.fullname = data["fullname"]
        if "qualification" in data:
            user.qualification = data["qualification"]
        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": "Error updating user"}), 500

@users_bp.route("/deleteuser/<int:id>", methods=["DELETE"])
@login_required
@staff_required
@protect_super_admin
def delete_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        if request.role == 'manager':
            if user.email_domain != request.user.email_domain:
                return jsonify({"message": "Access denied: User outside your domain"}), 403
            if user.role != 'user':
                return jsonify({"message": "Managers can only delete standard users"}), 403
            
        db.session.delete(user)
        ActivityLog.log(request.user_id, "Deleted User", f"Deleted user: {user.user_name} ({user.email})")
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": "Error deleting user"}), 500

@users_bp.route("/blockuser/<int:id>", methods=["POST"])
@login_required
@staff_required
@protect_super_admin
def block_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        if request.role == 'manager':
            if user.email_domain != request.user.email_domain:
                return jsonify({"message": "Access denied: User outside your domain"}), 403
            if user.role != 'user':
                return jsonify({"message": "Managers can only block standard users"}), 403
            
        if hasattr(user, 'is_blocked'):
            user.is_blocked = not user.is_blocked
            action = "Blocked User" if user.is_blocked else "Unblocked User"
            ActivityLog.log(request.user_id, action, f"{action}: {user.user_name}")
            db.session.commit()
            return jsonify({"message": f"User {action.lower()} successfully", "is_blocked": user.is_blocked}), 200
        else:
             return jsonify({"message": "Block functionality not supported by model"}), 501
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": "Error blocking user"}), 500

@users_bp.route("/dashboard_stats", methods=["GET"])
@login_required
def dashboard_stats():
    try:
        from app.models.score import Scores
        from app.models.mock_quiz import MockAttempt, MockQuiz
        from app.models.quiz import Quiz
        from app.models.question import Question
        from app.models.mock_quiz import MockQuestion
        from datetime import datetime

        user_id = request.user_id
        
        # 1. Standard Quizzes
        std_scores = Scores.query.filter_by(user_id=user_id).all()
        # 2. Mock Attempts
        mock_attempts = MockAttempt.query.filter_by(user_id=user_id).all()

        total_quizzes = len(std_scores) + len(mock_attempts)
        
        total_obtained = 0
        total_possible = 0
        
        # Calculate Standard Quiz Stats
        for s in std_scores:
            total_obtained += s.total_score
            # Calculate max possible for this quiz (count questions)
            q_count = Question.query.filter_by(quiz_id=s.quiz_id).count()
            total_possible += (q_count if q_count > 0 else 1) # Avoid div by zero

        # Calculate Mock Quiz Stats
        for m in mock_attempts:
            total_obtained += m.score
            # Calculate max possible
            # We need to query MockQuestions for this mock_quiz_id
            mq_count = MockQuestion.query.filter_by(mock_quiz_id=m.mock_quiz_id).count()
            # Assuming 1 mark per question for now implies total_possible += mq_count
            # If we used marks, we'd sum marks. Let's assume 1 mark per question for consistency in this quick refactor.
            total_possible += (mq_count if mq_count > 0 else 1)

        avg_score = 0
        if total_possible > 0:
            avg_score = round((total_obtained / total_possible) * 100, 1)

        # Days Active
        # Find earliest activity or fallback to 1
        dates = [s.timestamp for s in std_scores] + [m.submitted_at for m in mock_attempts]
        days_active = 0
        if dates:
            first_activity = min(dates)
            delta = datetime.utcnow() - first_activity
            days_active = delta.days + 1 # Include today
        
        # Recent Activity
        activities = []
        for s in std_scores:
            quiz = Quiz.query.get(s.quiz_id)
            activities.append({
                "type": "Standard",
                "title": quiz.name if quiz else "Unknown Quiz",
                "score": s.total_score,
                "date": s.timestamp
            })
        for m in mock_attempts:
            mq = MockQuiz.query.get(m.mock_quiz_id)
            activities.append({
                "type": "Mock",
                "title": mq.title if mq else "Unknown Mock Quiz",
                "score": m.score,
                "date": m.submitted_at
            })
            
        # Sort by date desc
        activities.sort(key=lambda x: x['date'], reverse=True)
        recent = activities[:5]
        # Format dates for JSON
        for a in recent:
            a['date'] = a['date'].strftime('%Y-%m-%d %H:%M')

        return jsonify({
            "total_quizzes": total_quizzes,
            "average_score": avg_score,
            "days_active": days_active,
            "recent_activity": recent
        }), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": "Error unblocking user"}), 500

@users_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    try:
        from app.models.score import Scores
        from app.models.mock_quiz import MockAttempt, MockQuiz
        from app.models.quiz import Quiz
        from app.models.question import Question
        from app.models.mock_quiz import MockQuestion
        from datetime import datetime

        user_id = request.user_id
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        activities = []
        # Calculate Stats (Similar logic to dashboard_stats)
        std_scores = Scores.query.filter_by(user_id=user_id).all()
        mock_attempts = MockAttempt.query.filter_by(user_id=user_id).all()

        total_quizzes = len(std_scores) + len(mock_attempts)
        
        total_obtained = 0
        total_possible = 0
        
        for s in std_scores:
            total_obtained += s.total_score
            q_count = Question.query.filter_by(quiz_id=s.quiz_id).count()
            total_possible += (q_count if q_count > 0 else 1)

        for m in mock_attempts:
            total_obtained += m.score
            mq_count = MockQuestion.query.filter_by(mock_quiz_id=m.mock_quiz_id).count()
            total_possible += (mq_count if mq_count > 0 else 1)

        avg_score = 0
        if total_possible > 0:
            avg_score = round((total_obtained / total_possible) * 100, 1)

        dates = [s.timestamp for s in std_scores] + [m.submitted_at for m in mock_attempts]
        days_active = 0
        if dates:
            first_activity = min(dates)
            delta = datetime.utcnow() - first_activity
            days_active = delta.days + 1 
        
        if user.isadmin:
            # For admin, show action tokens
            admin_logs = ActivityLog.query.filter_by(user_id=user_id).order_by(ActivityLog.timestamp.desc()).limit(10).all()
            for log in admin_logs:
                activities.append({
                    "type": "Action",
                    "title": log.action,
                    "details": log.details,
                    "date": log.timestamp.strftime('%Y-%m-%d %H:%M')
                })
        else:
            # For regular users, show quiz attempts
            for s in std_scores:
                quiz = Quiz.query.get(s.quiz_id)
                activities.append({
                    "type": "Standard",
                    "title": quiz.name if quiz else "Unknown Quiz",
                    "score": s.total_score,
                    "date": s.timestamp
                })
            for m in mock_attempts:
                mq = MockQuiz.query.get(m.mock_quiz_id)
                activities.append({
                    "type": "Mock",
                    "title": mq.title if mq else "Unknown Mock Quiz",
                    "score": m.score,
                    "date": m.submitted_at
                })
            
            activities.sort(key=lambda x: x['date'], reverse=True)
            activities = activities[:10]
            for a in activities:
                if isinstance(a['date'], datetime):
                    a['date'] = a['date'].strftime('%Y-%m-%d %H:%M')
        
        recent = activities # Already formatted and limited

        user_data = {
            "id": user.id,
            "username": user.user_name,
            "email": user.email,
            "fullname": user.fullname,
            "qualification": user.qualification,
            "dob": user.dob.strftime('%Y-%m-%d') if user.dob else "",
            "isadmin": user.isadmin,
            "role": user.role,
            "gemini_api_key": user.gemini_api_key,
            "bio": user.bio,
            "profile_picture": user.profile_picture,
            "social_github": user.social_github,
            "social_linkedin": user.social_linkedin,
            "social_instagram": user.social_instagram
        }

        stats = {
            "total_quizzes": total_quizzes,
            "average_score": avg_score,
            "days_active": days_active,
            "recent_activity": recent
        }

        return jsonify({"user": user_data, "stats": stats}), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": "Error fetching profile"}), 500

@users_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    try:
        user_id = request.user_id
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        data = request.get_json()

        if "fullname" in data:
            user.fullname = data["fullname"]
        if "qualification" in data:
            user.qualification = data["qualification"]
        if "bio" in data:
            user.bio = data["bio"]
        if "social_github" in data:
            user.social_github = data["social_github"]
        if "social_linkedin" in data:
            user.social_linkedin = data["social_linkedin"]
        if "social_instagram" in data:
            user.social_instagram = data["social_instagram"]
            
        if "dob" in data:
            try:
                from datetime import datetime
                if data["dob"]:
                    user.dob = datetime.strptime(data["dob"], '%Y-%m-%d').date()
            except ValueError:
                pass # Ignore invalid date format

        if "gemini_api_key" in data:
            new_key = data["gemini_api_key"]
            current_masked = user.gemini_api_key
            
            should_update = False
            # If no current key, always update
            if current_masked is None:
                should_update = True
            # If current key exists, only update if new key is different AND not the masked version itself
            elif new_key != current_masked:
                # Basic check to ensure we aren't just sending back the masked string
                # Masked strings usually contain ****
                if "****" not in new_key:
                    should_update = True
            
            if should_update:
                user.gemini_api_key = new_key
        
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": "Error updating profile"}), 500

@users_bp.route("/update_role/<int:user_id>", methods=["POST"])
@login_required
@staff_required
@protect_super_admin
def update_role(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Manager restrictions
        if request.role == 'manager':
            # Check domain
            if user.email_domain != request.user.email_domain:
                return jsonify({"message": "Access denied: User outside your domain"}), 403
            
            # Check new role
            data = request.get_json()
            new_role = data.get("role")
            if new_role == 'admin':
                return jsonify({"message": "Managers cannot assign admin role"}), 403
        else:
            data = request.get_json()
            new_role = data.get("role")
        
        if new_role not in ["admin", "manager", "user"]:
            return jsonify({"message": "Invalid role"}), 400
            
        user.role = new_role
        # Sync isadmin flag
        user.isadmin = (new_role == "admin")
        
        db.session.commit()
        ActivityLog.log(request.user_id, "Update Role", f"Changed role of {user.user_name} to {new_role}")
        return jsonify({
            "message": f"User role updated to {new_role}",
            "user": {
                "id": user.id,
                "role": user.role,
                "isadmin": user.isadmin
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": "Error updating role"}), 500

@users_bp.route("/profile-picture", methods=["POST"])
@login_required
def upload_profile_picture():
    try:
        if 'file' not in request.files:
            return jsonify({"message": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No selected file"}), 400
            
        if file:
            # Validate file extension
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            filename = file.filename
            if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return jsonify({"message": "Invalid file type"}), 400

            import os
            from werkzeug.utils import secure_filename
            
            # Setup uploads folder
            # Ideally this path should be in config, but using app instance path for now
            # static/uploads/profiles
            base_path = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
            os.makedirs(base_path, exist_ok=True)
            
            # Generate unique filename
            ext = filename.rsplit('.', 1)[1].lower()
            unique_name = f"user_{request.user_id}_{int(datetime.utcnow().timestamp())}.{ext}"
            file_path = os.path.join(base_path, unique_name)
            
            file.save(file_path)
            
            # Update user record
            user = User.query.get(request.user_id)
            # URL path relative to static
            # Assuming standard Flask static serving from /static
            web_path = f"/static/uploads/profiles/{unique_name}"
            user.profile_picture = web_path
            
            db.session.commit()
            
            return jsonify({"message": "Profile picture updated", "url": web_path}), 200
            
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": f"Error uploading image: {str(e)}"}), 500

@users_bp.route("/directory", methods=["GET"])
@login_required
def get_directory():
    try:
        user_id = request.user_id
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({"message": "User not found"}), 404
            
        domain = current_user.email_domain
        search_query = request.args.get('search', '').lower()
        
        # Base query: same domain, exclude admins unless you are admin (though admins might want to see each other, usually directory is for peers)
        # Requirement: "each user under a same institute... can view... each other"
        # So we show everyone in domain.
        
        query = User.query.filter(User.email.like(f"%@{domain}"))
        
        # Filter by search
        if search_query:
            query = query.filter(
                db.or_(
                    User.fullname.ilike(f"%{search_query}%"),
                    User.user_name.ilike(f"%{search_query}%"),
                    User.email.ilike(f"%{search_query}%")
                )
            )
            
        users = query.all()
        
        directory_list = []
        for u in users:
            # Hide self from list? Optional. Let's keep self for now so they see how they appear.
            directory_list.append({
                "id": u.id,
                "username": u.user_name,
                "fullname": u.fullname,
                "profile_picture": u.profile_picture,
                "qualification": u.qualification,
                "role": u.role,
                "bio": u.bio # Maybe show snippet
            })
            
        return jsonify({"users": directory_list}), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": "Error fetching directory"}), 500

@users_bp.route("/public-profile/<int:target_id>", methods=["GET"])
@login_required
def get_public_profile(target_id):
    try:
        # 1. Fetch Requestor and Target
        requestor = User.query.get(request.user_id)
        target = User.query.get(target_id)
        
        if not target:
            return jsonify({"message": "User not found"}), 404
            
        # 2. Check Domain Access
        # Allow if same domain OR requestor is global admin
        is_global_admin = (requestor.role == 'admin' or requestor.isadmin)
        if target.email_domain != requestor.email_domain and not is_global_admin:
            return jsonify({"message": "Profile not accessible"}), 403
            
        # 3. Fetch Stats (Public Subset)
        # We can reuse some logic or just do quick counts
        from app.models.score import Scores
        from app.models.mock_quiz import MockAttempt
        
        std_count = Scores.query.filter_by(user_id=target.id).count()
        mock_count = MockAttempt.query.filter_by(user_id=target.id).count()
        total_quizzes = std_count + mock_count
        
        # Avg Score logic simplified for public view (optional, or reuse robust logic)
        # Let's do a quick calc
        std_scores = Scores.query.filter_by(user_id=target.id).all()
        total_obtained = sum([s.total_score for s in std_scores])
        # Note: This crude avg doesn't account for max possible, but for public view maybe sufficient?
        # Actually user asked for "everything in profile page", so we should try to be accurate.
        # Let's call a helper or duplicate the robust logic for accuracy.
        
        # Reuse robust logic from dashboard_stats slightly adapted
        from app.models.question import Question
        from app.models.mock_quiz import MockQuestion
        
        mock_attempts = MockAttempt.query.filter_by(user_id=target.id).all()
        
        robust_possible = 0
        robust_obtained = 0
        
        for s in std_scores:
            robust_obtained += s.total_score
            q_count = Question.query.filter_by(quiz_id=s.quiz_id).count()
            robust_possible += (q_count if q_count > 0 else 1)
            
        for m in mock_attempts:
            robust_obtained += m.score
            mq_count = MockQuestion.query.filter_by(mock_quiz_id=m.mock_quiz_id).count()
            robust_possible += (mq_count if mq_count > 0 else 1)
            
        avg_score = 0
        if robust_possible > 0:
            avg_score = round((robust_obtained / robust_possible) * 100, 1)

        # 4. Construct Public Data
        public_data = {
            "id": target.id,
            "username": target.user_name,
            "fullname": target.fullname,
            "email": target.email, # Included as per request "everything... except api key"
            "qualification": target.qualification,
            "bio": target.bio,
            "profile_picture": target.profile_picture,
            "social_github": target.social_github,
            "social_linkedin": target.social_linkedin,
            "social_instagram": target.social_instagram,
            "role": target.role,
            "joined_at": target.created_at.strftime('%Y-%m-%d'),
            "stats": {
                "total_quizzes": total_quizzes,
                "average_score": avg_score
            }
        }
        
        return jsonify({"user": public_data}), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": "Error fetching public profile"}), 500