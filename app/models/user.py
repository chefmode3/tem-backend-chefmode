from sqlalchemy import JSON

from app.extensions import db
from datetime import datetime


class UserRecipe(db.Model):
    __tablename__ = 'user_recipe'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    flag = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='recipes_association')
    recipe = db.relationship('Recipe', back_populates='users_association')


class AnonymousUserRecipe(db.Model):
    __tablename__ = 'anonymous_user_recipe'
    anonymous_user_id = db.Column(db.Integer, db.ForeignKey('anonymous_user.id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    request_count = db.Column(db.Integer, default=0)

    anonymous_user = db.relationship('AnonymousUser', back_populates='recipes_association')
    recipe = db.relationship('Recipe', back_populates='anonymous_users_association')


class User(db.Model):

    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),  nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    activate = db.Column(db.Boolean, default=False)
    google_token = db.Column(db.String(255), unique=True, nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recipes_association = db.relationship('UserRecipe', back_populates='user')
    recipes = db.relationship('Recipe', secondary='user_recipe', back_populates='users')
    payments = db.relationship('Payment', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'

    def __init__(
            self,
            name,
            email,
            activate = False,
            password=None,
            google_token=None,
            google_id=None
    ):
        self.name = name
        self.email = email
        self.password = password
        self.activate = activate
        self.google_id = google_id
        self.google_token = google_token
        # self.subscription_id = subscription_id


class AnonymousUser(db.Model):
    __tablename__ = 'anonymous_user'
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(50), nullable=False, unique=True)

    recipes_association = db.relationship('AnonymousUserRecipe', back_populates='anonymous_user')
    recipes = db.relationship('Recipe', secondary='anonymous_user_recipe', back_populates='anonymous_users')


class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    origin = db.Column(db.String(255), nullable=False)
    servings = db.Column(db.Integer, nullable=True)
    preparation_time = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    users_association = db.relationship('UserRecipe', back_populates='recipe')
    users = db.relationship('User', secondary='user_recipe', back_populates='recipes')
    anonymous_users_association = db.relationship('AnonymousUserRecipe', back_populates='recipe')
    anonymous_users = db.relationship('AnonymousUser', secondary='anonymous_user_recipe', back_populates='recipes')

    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True)
    processes = db.relationship('Process', backref='recipe', lazy=True)



class Ingredient(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(20), nullable=True)

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)


class Process(db.Model):
    __tablename__ = 'process'
    id = db.Column(db.Integer, primary_key=True)
    step_number = db.Column(db.Integer, nullable=True)
    instructions = db.Column(db.Text, nullable=True)

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)


class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)