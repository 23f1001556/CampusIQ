from app.configs.extensions import db

class Subject(db.Model):
    __tablename__ = "subject"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False) # Removed unique=True globally
    description = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Cascade delete all chapters when a subject is deleted
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete')
