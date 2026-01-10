import os
import werkzeug
from flask import Blueprint, request, jsonify, current_app
from app.configs.extensions import db
from app.models import InstituteCourse, InstitutePaper, InstituteLecture, AIGeneratedContent, User
from app.auth.decors import login_required, staff_required
from datetime import datetime
import traceback

institute_bp = Blueprint('institute', __name__)

UPLOAD_FOLDER = os.path.join('app', 'uploads', 'institute')
ALLOWED_EXTENSIONS = {'pdf'}

# Self-healing column check for SQLite
def ensure_columns():
    with db.engine.connect() as conn:
        for table in ['institute_papers', 'institute_lectures']:
            result = conn.execute(db.text(f"PRAGMA table_info({table})"))
            columns = [row[1] for row in result]
            if 'file_path' not in columns:
                conn.execute(db.text(f"ALTER TABLE {table} ADD COLUMN file_path VARCHAR(500)"))
            if 'link_url' not in columns:
                conn.execute(db.text(f"ALTER TABLE {table} ADD COLUMN link_url VARCHAR(500)"))
        conn.commit()

# try:
#     ensure_columns()
# except Exception as e:
#     print(f"Column check failed: {e}")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Courses ---

@institute_bp.route('/courses', methods=['GET'])
@login_required
def get_courses():
    try:
        domain = request.user.email_domain
        courses = InstituteCourse.query.filter_by(domain=domain).all()
        return jsonify([{
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'created_at': c.created_at
        } for c in courses]), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"message": "An error occurred while fetching courses"}), 500

@institute_bp.route('/courses', methods=['POST'])
@staff_required
def create_course():
    try:
        data = request.get_json()
        new_course = InstituteCourse(
            title=data.get('title'),
            description=data.get('description'),
            domain=request.user.email_domain,
            created_by_id=request.user.id
        )
        db.session.add(new_course)
        db.session.commit()
        return jsonify({"message": "Course created successfully", "id": new_course.id}), 201
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"message": "An error occurred while creating the course"}), 500

@institute_bp.route('/courses/<int:id>', methods=['DELETE'])
@staff_required
def delete_course(id):
    try:
        course = InstituteCourse.query.get_or_404(id)
        if course.domain != request.user.email_domain:
            return jsonify({"message": "Forbidden: You cannot delete courses from other domains"}), 403
        
        # Cleanup files for papers and lectures
        for p in course.papers:
            if p.file_path:
                try: os.remove(os.path.join(os.getcwd(), 'backend', p.file_path))
                except: pass
        for l in course.lectures:
            if l.file_path:
                try: os.remove(os.path.join(os.getcwd(), 'backend', l.file_path))
                except: pass

        db.session.delete(course)
        db.session.commit()
        return jsonify({"message": "Course deleted successfully"}), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"message": "An error occurred while deleting the course"}), 500

# --- Papers & Lectures ---

@institute_bp.route('/courses/<int:course_id>/materials', methods=['GET'])
@login_required
def get_course_materials(course_id):
    try:
        course = InstituteCourse.query.get_or_404(course_id)
        if course.domain != request.user.email_domain:
            return jsonify({"message": "Forbidden: You cannot access materials from other domains"}), 403
        
        papers = [{
            'id': p.id,
            'title': p.title,
            'content': p.content,
            'file_path': p.file_path,
            'link_url': p.link_url,
            'created_at': p.created_at
        } for p in course.papers]
        
        lectures = [{
            'id': l.id,
            'title': l.title,
            'content': l.content,
            'video_url': l.video_url,
            'file_path': l.file_path,
            'link_url': l.link_url,
            'created_at': l.created_at
        } for l in course.lectures]
        
        return jsonify({
            'papers': papers,
            'lectures': lectures
        }), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"message": "An error occurred while fetching materials"}), 500

@institute_bp.route('/courses/<int:course_id>/paper', methods=['POST'])
@staff_required
def add_paper(course_id):
    try:
        course = InstituteCourse.query.get_or_404(course_id)
        if course.domain != request.user.email_domain:
            return jsonify({"message": "Forbidden"}), 403
        
        title = request.form.get('title')
        content = request.form.get('content')
        link_url = request.form.get('link_url')
        file_path = None

        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = f"paper_{datetime.now().timestamp()}_{werkzeug.utils.secure_filename(file.filename)}"
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                full_path = os.path.join(os.getcwd(), save_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                file.save(full_path)
                file_path = save_path

        new_paper = InstitutePaper(
            title=title,
            content=content,
            file_path=file_path,
            link_url=link_url,
            course_id=course_id
        )
        db.session.add(new_paper)
        db.session.commit()
        return jsonify({"message": "Paper added successfully", "id": new_paper.id}), 201
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"message": "An error occurred"}), 500

@institute_bp.route('/courses/<int:course_id>/lecture', methods=['POST'])
@staff_required
def add_lecture(course_id):
    try:
        course = InstituteCourse.query.get_or_404(course_id)
        if course.domain != request.user.email_domain:
            return jsonify({"message": "Forbidden"}), 403
        
        title = request.form.get('title')
        content = request.form.get('content')
        video_url = request.form.get('video_url')
        link_url = request.form.get('link_url')
        file_path = None

        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = f"lecture_{datetime.now().timestamp()}_{werkzeug.utils.secure_filename(file.filename)}"
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                full_path = os.path.join(os.getcwd(), save_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                file.save(full_path)
                file_path = save_path

        new_lecture = InstituteLecture(
            title=title,
            content=content,
            video_url=video_url,
            file_path=file_path,
            link_url=link_url,
            course_id=course_id
        )
        db.session.add(new_lecture)
        db.session.commit()
        return jsonify({"message": "Lecture added successfully", "id": new_lecture.id}), 201
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"message": "An error occurred"}), 500

# --- Update & Delete Materials ---

@institute_bp.route('/paper/<int:id>', methods=['PUT', 'DELETE'])
@staff_required
def manage_paper(id):
    try:
        paper = InstitutePaper.query.get_or_404(id)
        if paper.course.domain != request.user.email_domain:
            return jsonify({"message": "Forbidden"}), 403

        if request.method == 'DELETE':
            if paper.file_path:
                try: os.remove(os.path.join(os.getcwd(), 'backend', paper.file_path))
                except: pass
            db.session.delete(paper)
            db.session.commit()
            return jsonify({"message": "Paper deleted"}), 200

        data = request.get_json()
        paper.title = data.get('title', paper.title)
        paper.content = data.get('content', paper.content)
        paper.link_url = data.get('link_url', paper.link_url)
        db.session.commit()
        return jsonify({"message": "Paper updated"}), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"message": "Error managing paper"}), 500

@institute_bp.route('/lecture/<int:id>', methods=['PUT', 'DELETE'])
@staff_required
def manage_lecture(id):
    try:
        lecture = InstituteLecture.query.get_or_404(id)
        if lecture.course.domain != request.user.email_domain:
            return jsonify({"message": "Forbidden"}), 403

        if request.method == 'DELETE':
            if lecture.file_path:
                try: os.remove(os.path.join(os.getcwd(), 'backend', lecture.file_path))
                except: pass
            db.session.delete(lecture)
            db.session.commit()
            return jsonify({"message": "Lecture deleted"}), 200

        data = request.get_json()
        lecture.title = data.get('title', lecture.title)
        lecture.content = data.get('content', lecture.content)
        lecture.video_url = data.get('video_url', lecture.video_url)
        lecture.link_url = data.get('link_url', lecture.link_url)
        db.session.commit()
        return jsonify({"message": "Lecture updated"}), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"message": "Error managing lecture"}), 500

# --- File Serving ---

@institute_bp.route('/files/<path:filename>')
@login_required
def serve_file(filename):
    # Ensure domain check for security
    # In a real app we'd verify the file belongs to a course in the user's domain
    # For now we'll use flask's send_from_directory
    from flask import send_from_directory
    return send_from_directory(os.path.join(os.getcwd(), 'backend', 'app', 'uploads', 'institute'), filename)

# --- AI Tools (Stubs) ---
# ... (rest of the file)

# --- AI Tools (Stubs for now, will integrate Gemini) ---

@institute_bp.route('/ai/summarize', methods=['POST'])
@login_required
def ai_summarize():
    try:
        data = request.get_json()
        # In a real app, we'd call Gemini here. For now, a mock response.
        summary = f"Summary of {data.get('title')}: This is a high-level overview of the content provided in the lecture/paper."
        
        new_note = AIGeneratedContent(
            user_id=request.user.id,
            source_type=data.get('type'),
            source_id=data.get('id'),
            content=summary,
            content_type='summary'
        )
        db.session.add(new_note)
        db.session.commit()
        
        return jsonify({"summary": summary, "id": new_note.id}), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"message": "AI Summarization failed"}), 500

@institute_bp.route('/ai/generate-quiz', methods=['POST'])
@login_required
def ai_generate_quiz():
    try:
        data = request.get_json()
        # Mocking AI quiz generation.
        quiz_data = "AI Quiz: 1. Question? A) Ans1 B) Ans2 ..."
        
        new_quiz = AIGeneratedContent(
            user_id=request.user.id,
            source_type=data.get('type'),
            source_id=data.get('id'),
            content=quiz_data,
            content_type='quiz'
        )
        db.session.add(new_quiz)
        db.session.commit()
        
        return jsonify({"quiz": quiz_data, "id": new_quiz.id}), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"message": "AI Quiz generation failed"}), 500

@institute_bp.route('/ai/saved', methods=['GET'])
@login_required
def get_saved_content():
    try:
        saved = AIGeneratedContent.query.filter_by(user_id=request.user.id).all()
        return jsonify([{
            'id': s.id,
            'source_type': s.source_type,
            'content': s.content,
            'content_type': s.content_type,
            'created_at': s.created_at
        } for s in saved]), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"message": "Failed to fetch saved content"}), 500
