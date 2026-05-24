from app.configs.extensions import db
from datetime import datetime

class StudyMaterial(db.Model):
    __tablename__ = "study_materials"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Linked to Subject and Chapter
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=True) # Optional chapter
    quiz_name = db.Column(db.String(150), nullable=True) # Optional quiz name
    
    # New fields for PDFs and Links
    material_type = db.Column(db.String(50), default='text') # 'text', 'pdf', 'link'
    file_path = db.Column(db.String(500), nullable=True)     # For PDFs
    link_url = db.Column(db.String(500), nullable=True)      # For external links
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subject = db.relationship('Subject', backref='materials')
    chapter = db.relationship('Chapter', backref='materials')
