
from extensions import db
from datetime import datetime

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    resume_text = db.Column(db.Text, nullable=False)
    resume_file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"<Resume {self.name}>"

    def __init__(self, name, resume_text, resume_file_path, user_id):
        self.name = name
        self.resume_text = resume_text
        self.resume_file_path = resume_file_path
        self.user_id = user_id