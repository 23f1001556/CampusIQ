from app.configs.extensions import db
from datetime import datetime

class ActivityLog(db.Model):
    __tablename__ = "activity_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to user
    user = db.relationship("User", backref="activity_logs")

    @staticmethod
    def log(user_id, action, details=None):
        try:
            new_log = ActivityLog(user_id=user_id, action=action, details=details)
            db.session.add(new_log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to log activity: {e}")
