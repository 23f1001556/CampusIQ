from flask import Blueprint, jsonify, request
from app.configs.extensions import db
from app.models.chapter import Chapter
from app.models.subject import Subject

from app.auth.decors import login_required

chapters_bp = Blueprint("chapters", __name__, url_prefix="/chapters")

@chapters_bp.route("/createchapter", methods=["POST"])
@login_required
def create_chapter():
    try:
        data = request.get_json()
        chapter_name = data.get("chapter_name")
        description = data.get("description")
        subject_id = data.get("subject_id")

        if not chapter_name or not subject_id:
            return jsonify({"message": "Missing required fields: 'chapter_name' and 'subject_id'"}), 400

        # Verify subject exists and belongs to user
        subject = Subject.query.filter_by(id=subject_id, user_id=request.user_id).first()
        if not subject:
            return jsonify({"message": "Subject not found or access denied"}), 404

        new_chapter = Chapter(
            name=chapter_name,
            description=description,
            subject_id=subject_id
        )
        db.session.add(new_chapter)
        db.session.commit()
        
        return jsonify({"message": "Chapter created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@chapters_bp.route("/updatechapter/<int:id>", methods=["PUT"])
@login_required
def update_chapter(id):
    try:
        # Check ownership via join
        chapter = Chapter.query.join(Subject).filter(Chapter.id == id, Subject.user_id == request.user_id).first()
        if not chapter:
            return jsonify({"message": "Chapter not found or access denied"}), 404
            
        data = request.get_json()
        new_name = data.get("chapter_name")
        new_description = data.get("description")
        
        if new_name:
            chapter.name = new_name
        if new_description:
            chapter.description = new_description
            
        db.session.commit()
        return jsonify({"message": "Chapter updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@chapters_bp.route("/getchapters", methods=["GET"])
@login_required
def get_chapters():
    try:
        all_chapters = Chapter.query.join(Subject).filter(Subject.user_id == request.user_id).all()
        output = []
        for chap in all_chapters:
            output.append({
                "id": chap.id,
                "name": chap.name,
                "description": chap.description,
                "subject_id": chap.subject_id,
                "subject_name": chap.subject.name if chap.subject else None,
                "quiz_count": len(chap.quizzes)
            })
        return jsonify({"chapters": output}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@chapters_bp.route("/getchapters/<int:subject_id>", methods=["GET"])
@login_required
def get_chapters_by_subject(subject_id):
    try:
        # Verify subject belongs to user
        subject = Subject.query.filter_by(id=subject_id, user_id=request.user_id).first()
        if not subject:
            return jsonify({"message": "Subject not found or access denied"}), 404

        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        output = []
        for chap in chapters:
            output.append({
                "id": chap.id,
                "name": chap.name,
                "description": chap.description,
                "subject_id": chap.subject_id
            })
        return jsonify({"chapters": output}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@chapters_bp.route("/getchapter/<int:id>", methods=["GET"])
@login_required
def get_chapter(id):
    try:
        chapter = Chapter.query.join(Subject).filter(Chapter.id == id, Subject.user_id == request.user_id).first()
        if not chapter:
            return jsonify({"message": "Chapter not found or access denied"}), 404
            
        chapter_data = {
            "id": chapter.id,
            "name": chapter.name,
            "description": chapter.description,
            "subject_id": chapter.subject_id,
            "subject_name": chapter.subject.name if chapter.subject else None,
            "quiz_count": len(chapter.quizzes)
        }
        return jsonify({"chapter": chapter_data}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@chapters_bp.route("/deletechapter/<int:id>", methods=["DELETE"])
@login_required
def delete_chapter(id):
    try:
        chapter = Chapter.query.join(Subject).filter(Chapter.id == id, Subject.user_id == request.user_id).first()
        if not chapter:
            return jsonify({"message": "Chapter not found or access denied"}), 404
            
        db.session.delete(chapter)
        db.session.commit()
        return jsonify({"message": "Chapter deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
