from app.configs.extensions import db
from datetime import datetime
import json

class MockQuiz(db.Model):
    __tablename__ = "mock_quiz"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    
    questions = db.relationship('MockQuestion', backref='mock_quiz', cascade='all, delete-orphan')
    attempts = db.relationship('MockAttempt', backref='mock_quiz', cascade='all, delete-orphan')

class MockQuestion(db.Model):
    __tablename__ = "mock_question"
    
    id = db.Column(db.Integer, primary_key=True)
    mock_quiz_id = db.Column(db.Integer, db.ForeignKey('mock_quiz.id'), nullable=False)
    statement = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.String(255), nullable=False)
    option_2 = db.Column(db.String(255), nullable=False)
    option_3 = db.Column(db.String(255), nullable=False)
    option_4 = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(50), nullable=False) # "1", "2", "3", "4"
    marks = db.Column(db.Integer, default=1)

class MockAttempt(db.Model):
    __tablename__ = "mock_attempt"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mock_quiz_id = db.Column(db.Integer, db.ForeignKey('mock_quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=True) # Nullable until submitted
    # Storing answers as JSON string: {"question_id": "selected_option"}
    _answers = db.Column("answers", db.Text, nullable=True) # Nullable until submitted
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship("User", backref="mock_attempts")

    @property
    def answers(self):
        if self._answers is None:
            return {}
        return json.loads(self._answers)
    
    @answers.setter
    def answers(self, value):
        self._answers = json.dumps(value)
