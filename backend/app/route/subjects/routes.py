from flask import Blueprint, jsonify, request
from app.auth.decors import login_required
from app.models.subject import Subject
from app.models.activity import ActivityLog
from app.configs.extensions import db

subjects_bp = Blueprint("subjects", __name__, url_prefix="/subjects")

@subjects_bp.route("/createsubject", methods=["POST"])
@login_required
def create_subject():
    try:
        data = request.get_json()
        subject_name = data.get("subject_name")
        description = data.get("description") # Get description
        
        if not subject_name:
             return jsonify({"message": "Missing required field: 'subject_name'"}), 400

        existing_subject = Subject.query.filter_by(name=subject_name, user_id=request.user_id).first()
        if existing_subject:
            return jsonify({"message": "Subject already exists"}), 400
    
        new_subject = Subject(name=subject_name, description=description, user_id=request.user_id)
        db.session.add(new_subject)
        ActivityLog.log(request.user_id, "Created Subject", f"Created subject: {subject_name}")
        db.session.commit()
        
        return jsonify({"message": "Subject created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@subjects_bp.route("/updatesubject/<int:id>", methods=["PUT"])
@login_required
def update_subject(id):
    try:
        subject = Subject.query.filter_by(id=id, user_id=request.user_id).first()
        if not subject:
            return jsonify({"message": "subject not found or access denied"}), 404
            
        data = request.get_json()
        new_name = data.get("subject_name")
        new_description = data.get("description")
        
        if new_name:
             if len(new_name) < 3: 
                pass # validation logic if needed
             subject.name = new_name
             
        if new_description is not None:
            subject.description = new_description

        db.session.commit()
        return jsonify({"message": "Subject updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@subjects_bp.route("/getsubjects", methods=["GET"])
@login_required
def get_subjects():
    try:
        all_subjects = Subject.query.filter_by(user_id=request.user_id).all()
        
        # Serialize
        output = []
        for sub in all_subjects:
            output.append({
                "id": sub.id,
                "name": sub.name,
                "description": sub.description,
                "chapter_count": len(sub.chapters)
            })
        return jsonify({"subjects": output}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@subjects_bp.route("/getsubject/<int:id>", methods=["GET"])
@login_required
def get_subject(id):
    try:
        subject = Subject.query.filter_by(id=id, user_id=request.user_id).first()
        if not subject:
             return jsonify({"message": "subject not found or access denied"}), 404
             
        # Serialize
        subject_data = {
            "id": subject.id,
            "name": subject.name,
            "description": subject.description,
            "chapter_count": len(subject.chapters)
        }
        return jsonify({"subject": subject_data}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@subjects_bp.route("/deletesubject/<int:id>", methods=["DELETE"])
@login_required
def delete_subject(id):
    try:
        subject = Subject.query.filter_by(id=id, user_id=request.user_id).first()
        if not subject:
            return jsonify({"message": "subject not found or access denied"}), 404
            
        db.session.delete(subject)
        ActivityLog.log(request.user_id, "Deleted Subject", f"Deleted subject: {subject.name}")
        db.session.commit()
        return jsonify({"message": "Subject deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
