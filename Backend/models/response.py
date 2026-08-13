from extensions import db
from datetime import datetime

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    author = db.relationship('User', backref=db.backref('responses', lazy=True))
    complaint = db.relationship('Complaint', backref=db.backref('responses', lazy=True, cascade="all, delete-orphan"))
