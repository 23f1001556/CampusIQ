from app.configs.extensions import db

class Chapter(db.Model):
    __tablename__ = "chapter"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    
    # Cascade delete all quizzes when a chapter is deleted
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete')

    # Cascade delete all questions when a chapter is deleted
    questions = db.relationship('Question', backref='chapter', lazy=True, cascade='all, delete')
