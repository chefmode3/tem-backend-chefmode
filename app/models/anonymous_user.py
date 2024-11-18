from app.extensions import db


class AnonymousUser(db.Model):
    __tablename__ = 'anonymous_user'
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(50), nullable=False, unique=True)
    request_count = db.Column(db.Integer, default=0)

    recipes_association = db.relationship('AnonymousUserRecipe', back_populates='anonymous_user')
    recipes = db.relationship('Recipe', secondary='anonymous_user_recipe', back_populates='anonymous_users')
