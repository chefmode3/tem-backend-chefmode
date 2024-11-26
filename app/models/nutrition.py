import uuid

from app.extensions import db


class Nutrition(db.Model):
    __tablename__ = 'nutritions'

    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)

    # recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=True)
    # nutrition = db.relationship('Recipe', back_populates='nutrition', uselist=True)
