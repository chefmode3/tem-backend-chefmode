from app.extensions import db
from pygments.lexer import default


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    origin = db.Column(db.String(255), nullable=False)
    servings = db.Column(db.Integer, nullable=True)
    flag = db.Column(db.Boolean, default=False)
    preparation_time = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    ingredients = db.Column(db.JSON, nullable=True)
    processes = db.Column(db.JSON, nullable=True)

    # Relationships
    users_association = db.relationship('UserRecipe', back_populates='recipe')

    anonymous_users_association = db.relationship('AnonymousUserRecipe', back_populates='recipe')

