import uuid

from app.extensions import db
from datetime import datetime


class Payment(db.Model):
    __tablename__ = 'payment'

    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50))

    # Relationships
    user_id = db.Column(db.String(255), db.ForeignKey('user.id'), nullable=False)
