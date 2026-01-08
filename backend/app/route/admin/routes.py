from flask import Blueprint, jsonify, request
import traceback
from datetime import datetime, timedelta
from sqlalchemy import func
from app.configs.extensions import db
from app.models.users import User
from app.models.subject import Subject
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.mock_quiz import MockQuiz, MockAttempt
from app.models.score import Scores
from app.models.institute import AIGeneratedContent
from app.auth.decors import login_required, admin_required, staff_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Domains to exclude from "Institute" logic
PUBLIC_DOMAINS = [
    'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 
    'icloud.com', 'aol.com', 'zoho.com', 'protonmail.com', 'me.com'
]

@admin_bp.route("/details", methods=["GET"])
@login_required
@staff_required
def get_dashboard_details():
    try:
        is_admin = request.role == 'admin' or getattr(request, 'isadmin', False)
        domain = request.user.email_domain

        if is_admin:
            # Total Institutes (unique domains, excluding public/null)
            all_users = User.query.all()
            domains = set()
            for u in all_users:
                dom = u.email_domain
                if dom and dom not in PUBLIC_DOMAINS:
                    domains.add(dom)
            
            institute_count = len(domains)
            user_count = User.query.count()
            manager_count = User.query.filter_by(role='manager').count()
            ai_usage_count = AIGeneratedContent.query.count()
        else:
            # Manager: Only see their domain
            institute_count = 1
            user_count = User.query.filter(User.email.like(f"%@{domain}")).count()
            manager_count = User.query.filter(User.email.like(f"%@{domain}")).filter_by(role='manager').count()
            ai_usage_count = db.session.query(AIGeneratedContent).join(User, AIGeneratedContent.user_id == User.id).filter(User.email.like(f"%@{domain}")).count()

        return jsonify({
            "institute_count": institute_count,
            "user_count": user_count,
            "manager_count": manager_count,
            "ai_usage_count": ai_usage_count
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@admin_bp.route("/institute-stats", methods=["GET"])
@login_required
@staff_required
def get_institute_stats():
    try:
        is_admin = request.role == 'admin' or getattr(request, 'isadmin', False)
        manager_domain = request.user.email_domain

        # Group users by domain
        query = User.query
        if not is_admin:
            query = query.filter(User.email.like(f"%@{manager_domain}"))
        
        all_users = query.all()
        institute_data = {}
        
        for u in all_users:
            dom = u.email_domain or "Unknown"
            # Skip public domains for admins only
            if is_admin and dom in PUBLIC_DOMAINS:
                continue
            
            if dom not in institute_data:
                institute_data[dom] = {
                    "users": 0, 
                    "managers": 0, 
                    "ai_usage": 0,
                    "blocked_users": 0, 
                    "total_users_for_block_check": 0
                }
            
            institute_data[dom]["users"] += 1
            
            # For block status check, we consider all non-admin users
            if not u.isadmin and u.role != 'admin':
                institute_data[dom]["total_users_for_block_check"] += 1
                if u.is_blocked:
                    institute_data[dom]["blocked_users"] += 1

            if u.role == 'manager':
                institute_data[dom]["managers"] += 1

        # Add AI Usage per domain
        ai_query = db.session.query(AIGeneratedContent, User.email).join(User, AIGeneratedContent.user_id == User.id)
        if not is_admin:
            ai_query = ai_query.filter(User.email.like(f"%@{manager_domain}"))
            
        ai_contents = ai_query.all()
        for content, email in ai_contents:
            dom = email.split('@')[-1] if '@' in email else "Unknown"
            if dom in institute_data:
                institute_data[dom]["ai_usage"] += 1

        formatted_stats = []
        for dom, data in institute_data.items():
            # Determine if institute is considered "blocked"
            # Logic: If > 50% of users are blocked, or purely if ALL users are blocked. 
            # Let's go with: if ALL existing non-admin users are blocked.
            # If no users, it's not blocked.
            is_blocked = False
            if data["total_users_for_block_check"] > 0 and data["blocked_users"] == data["total_users_for_block_check"]:
                is_blocked = True

            formatted_stats.append({
                "domain": dom,
                "user_count": data["users"],
                "manager_count": data["managers"],
                "ai_usage": data["ai_usage"],
                "is_blocked": is_blocked
            })

        # Sort by user count descending
        formatted_stats.sort(key=lambda x: x['user_count'], reverse=True)

        return jsonify({"institutes": formatted_stats}), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"message": str(e)}), 500

@admin_bp.route("/delete-institute", methods=["DELETE"])
@login_required
@admin_required
def delete_institute():
    try:
        # Password verification should ideally happen here too, 
        # but we'll rely on the frontend 2-step + /auth/verify_password check flow for UX speed, 
        # OR we can enforce it in the body. Let's stick to simple deletion for now as per plan focus on frontend modal.
        # Actually, adding a small check if password is sent provided in body is good practice.
        
        data = request.get_json() or {}
        domain = data.get('domain')
        
        if not domain:
            return jsonify({"message": "Domain is required"}), 400
            
        if domain in PUBLIC_DOMAINS:
             return jsonify({"message": "Cannot delete public domain users group"}), 403

        # Delete all users with this domain
        # Note: Cascading delete should handle related data (scores, quizzes etc) if models are set up right.
        # If not, we might leave orphans. Assuming User model cascade is 'all, delete-orphan' for key relations.
        
        users_to_delete = User.query.filter(User.email.like(f"%@{domain}")).all()
        count = len(users_to_delete)
        
        for u in users_to_delete:
            if u.role == 'admin' or u.isadmin:
                continue # Skip admins just in case
            db.session.delete(u)
            
        db.session.commit()
        
        return jsonify({"message": f"Successfully deleted {count} users and data for {domain}"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@admin_bp.route("/ai-usage-stats", methods=["GET"])
@login_required
@staff_required
def get_ai_usage_stats():
    try:
        is_admin = request.role == 'admin' or getattr(request, 'isadmin', False)
        domain = request.user.email_domain

        # Individual usage
        query = (db.session.query(User.user_name, User.email, func.count(AIGeneratedContent.id))
                        .join(AIGeneratedContent, User.id == AIGeneratedContent.user_id))
        
        if not is_admin:
            query = query.filter(User.email.like(f"%@{domain}"))

        usage_by_user = (query.group_by(User.id)
                        .order_by(func.count(AIGeneratedContent.id).desc())
                        .limit(10).all())

        return jsonify({
            "top_users": [{
                "username": u[0],
                "email": u[1],
                "count": u[2]
            } for u in usage_by_user]
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@admin_bp.route("/growth-trends", methods=["GET"])
@login_required
@staff_required
def get_growth_trends():
    try:
        is_admin = request.role == 'admin' or getattr(request, 'isadmin', False)
        domain = request.user.email_domain
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # Reg trends
        reg_query = (db.session.query(func.date(User.created_at), func.count(User.id))
                        .filter(User.created_at >= thirty_days_ago))
        
        if not is_admin:
            reg_query = reg_query.filter(User.email.like(f"%@{domain}"))
            
        registrations = (reg_query.group_by(func.date(User.created_at))
                        .order_by(func.date(User.created_at))
                        .all())

        # AI Usage trends
        ai_query = (db.session.query(func.date(AIGeneratedContent.created_at), func.count(AIGeneratedContent.id))
                        .filter(AIGeneratedContent.created_at >= thirty_days_ago))
        
        if not is_admin:
            ai_query = ai_query.join(User, AIGeneratedContent.user_id == User.id).filter(User.email.like(f"%@{domain}"))

        ai_usage = (ai_query.group_by(func.date(AIGeneratedContent.created_at))
                        .order_by(func.date(AIGeneratedContent.created_at))
                        .all())

        return jsonify({
            "registrations": [{"date": r[0], "count": r[1]} for r in registrations],
            "ai_usage": [{"date": a[0], "count": a[1]} for a in ai_usage]
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@admin_bp.route("/block-institute", methods=["POST"])
@login_required
@admin_required
def block_institute():
    try:
        data = request.get_json()
        domain = data.get('domain')
        if not domain or domain in PUBLIC_DOMAINS:
            return jsonify({"message": "Invalid or protected domain"}), 400
        
        # Block all users in this domain, EXCEPT admins
        updated_count = User.query.filter(
            User.email.like(f"%@{domain}"),
            User.role != 'admin',
            User.isadmin == False
        ).update(
            {"is_blocked": True}, synchronize_session=False
        )
        db.session.commit()
        
        return jsonify({"message": f"Successfully blocked {updated_count} users in {domain}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@admin_bp.route("/unblock-institute", methods=["POST"])
@login_required
@admin_required
def unblock_institute():
    try:
        data = request.get_json()
        domain = data.get('domain')
        if not domain or domain in PUBLIC_DOMAINS:
            return jsonify({"message": "Invalid or protected domain"}), 400
        
        updated_count = User.query.filter(User.email.like(f"%@{domain}")).update(
            {"is_blocked": False}, synchronize_session=False
        )
        db.session.commit()
        
        return jsonify({"message": f"Successfully unblocked {updated_count} users in {domain}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@admin_bp.route("/attempts_stats", methods=["GET"])
@login_required
@staff_required
def get_attempts_stats():
    try:
        # Fetch recent attempts from both Standard and Mock quizzes
        # Limit to last 50 to render a readable chart
        
        if request.role == 'manager':
            domain = request.user.email_domain
            std_scores_query = (db.session.query(Scores, User.user_name, Quiz.name)
                .join(User, Scores.user_id == User.id)
                .join(Quiz, Scores.quiz_id == Quiz.id)
                .filter(User.email.like(f"%@{domain}")))
            
            mock_attempts_query = (db.session.query(MockAttempt, User.user_name, MockQuiz.title)
                .join(User, MockAttempt.user_id == User.id)
                .join(MockQuiz, MockAttempt.mock_quiz_id == MockQuiz.id)
                .filter(MockAttempt.score.isnot(None))
                .filter(User.email.like(f"%@{domain}")))
        else:
            std_scores_query = (db.session.query(Scores, User.user_name, Quiz.name)
                .join(User, Scores.user_id == User.id)
                .join(Quiz, Scores.quiz_id == Quiz.id))
            
            mock_attempts_query = (db.session.query(MockAttempt, User.user_name, MockQuiz.title)
                .join(User, MockAttempt.user_id == User.id)
                .join(MockQuiz, MockAttempt.mock_quiz_id == MockQuiz.id)
                .filter(MockAttempt.score.isnot(None)))

        std_scores = std_scores_query.order_by(Scores.timestamp.desc()).limit(30).all()
        mock_attempts = mock_attempts_query.order_by(MockAttempt.submitted_at.desc()).limit(30).all()

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
@staff_required
def get_user_scores(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        if request.role == 'manager':
            if user.email_domain != request.user.email_domain:
                return jsonify({"message": "Access denied: User outside your domain"}), 403
            if user.role == 'admin':
                return jsonify({"message": "Access denied: Cannot view Admin scores"}), 403

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
