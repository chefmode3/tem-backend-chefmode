import uuid
from datetime import datetime

from app.extensions import db


class AnonymousUser(db.Model):
    __tablename__ = 'anonymous_user'
    id = db.Column(db.String(512), primary_key=True, default=lambda: str(uuid.uuid4()))
    identifier = db.Column(db.String(512), nullable=True, unique=True)

    request_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recipes_association = db.relationship('AnonymousUserRecipe', back_populates='anonymous_user')
