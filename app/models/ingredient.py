import uuid

from app.extensions import db


class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(255), nullable=False)
    recipe_id = db.Column(db.String(255), db.ForeignKey('recipes.id'), nullable=False)
    nutrition_id = db.Column(db.String(255), db.ForeignKey('nutritions.id'), nullable=False)
    
    # Relationships
    # recipe = db.relationship('Recipe', back_populates='ingredients')
    # nutrition = db.relationship('Nutrition', back_populates='ingredient', uselist=False)
    #
