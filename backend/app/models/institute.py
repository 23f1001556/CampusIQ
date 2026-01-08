from app.configs.extensions import db
from datetime import datetime

class InstituteCourse(db.Model):
    __tablename__ = "institute_courses"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    domain = db.Column(db.String(100), nullable=False) # e.g. 'example.com'
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    papers = db.relationship('InstitutePaper', backref='course', lazy=True, cascade="all, delete-orphan")
    lectures = db.relationship('InstituteLecture', backref='course', lazy=True, cascade="all, delete-orphan")

class InstitutePaper(db.Model):
    __tablename__ = "institute_papers"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True) # Optional text/description
    file_path = db.Column(db.String(500), nullable=True) # Path to PDF
    link_url = db.Column(db.String(500), nullable=True) # External link
    course_id = db.Column(db.Integer, db.ForeignKey('institute_courses.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InstituteLecture(db.Model):
    __tablename__ = "institute_lectures"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True) # Lecture notes/description
    video_url = db.Column(db.String(500), nullable=True)
    file_path = db.Column(db.String(500), nullable=True) # Path to PDF
    link_url = db.Column(db.String(500), nullable=True) # External link
    course_id = db.Column(db.Integer, db.ForeignKey('institute_courses.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AIGeneratedContent(db.Model):
    __tablename__ = "ai_generated_content"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source_type = db.Column(db.String(50)) # 'paper' or 'lecture'
    source_id = db.Column(db.Integer)
    content = db.Column(db.Text, nullable=False) # AI response content
    content_type = db.Column(db.String(50)) # 'summary' or 'quiz'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
