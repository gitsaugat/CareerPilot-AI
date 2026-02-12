from extensions import db
from datetime import datetime

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False) # Can store HTML
    company = db.Column(db.String(150), nullable=True)
    job_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), default='Saved') # Saved, Applied, Interviewing, Offer, Rejected
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Job {self.title}>'
