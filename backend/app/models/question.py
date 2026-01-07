from app.configs.extensions import db

class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.String(255), nullable=False)
    option_2 = db.Column(db.String(255), nullable=False)
    option_3 = db.Column(db.String(255), nullable=False)
    option_4 = db.Column(db.String(255), nullable=False)
    # Changed to String to support multiple correct options (e.g., "1,2")
    correct_option = db.Column(db.String(50), nullable=False)
    # New field to distinguish between single and multi choice
    question_type = db.Column(db.String(20), default="single", nullable=False)

    # String reference
    quiz = db.relationship("Quiz", back_populates="questions")
