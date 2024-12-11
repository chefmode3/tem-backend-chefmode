from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime

from app.extensions import db


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    origin = db.Column(db.String(255), nullable=False)
    servings = db.Column(db.Integer, nullable=True)
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)

    preparation_time = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    unit_serving = db.Column(db.String(255), nullable=True)

    ingredients = db.Column(db.JSON, nullable=True)
    processes = db.Column(db.JSON, nullable=True)
    nutritions = db.Column(db.JSON, nullable=True)

    # Relationships
    users_association = db.relationship('UserRecipe', back_populates='recipe')
    anonymous_users_association = db.relationship('AnonymousUserRecipe', back_populates='recipe')
