import uuid

from app.extensions import db


class AnonymousUser(db.Model):
    __tablename__ = 'anonymous_user'
    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    identifier = db.Column(db.String(50), nullable=False, unique=True)
    request_count = db.Column(db.Integer, default=0)

    recipes_association = db.relationship('AnonymousUserRecipe', back_populates='anonymous_user')
