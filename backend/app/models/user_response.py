from app.configs.extensions import db

class UserResponse(db.Model):
    __tablename__ = "user_responses"
    
    id = db.Column(db.Integer, primary_key=True)
    score_id = db.Column(db.Integer, db.ForeignKey('scores.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option = db.Column(db.String(10), nullable=True) # "1", "2", "3", "4" or null if skipped

    # Relationships can be added if needed, but simple ID linking is enough for now
