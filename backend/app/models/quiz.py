from app.configs.extensions import db
from datetime import datetime

class Quiz(db.Model):
    __tablename__ = "quiz"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"), nullable=False)
    date_of_quiz = db.Column(db.DateTime, default=datetime.utcnow)
    time_duration = db.Column(db.Integer) # Duration in minutes
    remarks = db.Column(db.Text)

    # string reference
    questions = db.relationship("Question", back_populates="quiz", cascade="all, delete")
    scores = db.relationship("Scores", backref="quiz", cascade="all, delete")

    # Publishing fields
    is_published = db.Column(db.Boolean, default=False)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    scores_released = db.Column(db.Boolean, default=False)
