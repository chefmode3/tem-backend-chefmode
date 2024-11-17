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

    anonymous_user = db.relationship('AnonymousUser', back_populates='recipes_association')
    recipe = db.relationship('Recipe', back_populates='anonymous_users_association')


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),  nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    activate = db.Column(db.Boolean, default=False)
    google_token = db.Column(db.String(255), unique=True, nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recipes_association = db.relationship(
        'UserRecipe',
        back_populates='user',
        overlaps="recipes"
    )
    recipes = db.relationship(
        'Recipe',
        secondary='user_recipe',
        back_populates='users',
        overlaps="recipes_association,user"
    )
    payments = db.relationship('Payment', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'

    def __init__(
            self,
            id,
            name,
            email,
            activate = False,
            password=None,
            google_token=None,
            google_id=None
    ):
        self.id = id
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

    recipes_association = db.relationship(
        'AnonymousUserRecipe',
        back_populates='anonymous_user',
        overlaps="recipes"
    )
    recipes = db.relationship(
        'Recipe',
        secondary='anonymous_user_recipe',
        back_populates='anonymous_users',
        overlaps="recipes_association,anonymous_user"
    )


class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    origin = db.Column(db.String(255), nullable=False)
    servings = db.Column(db.Integer, nullable=True)
    flag = db.Column(db.Boolean, default=False)
    preparation_time = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    users_association = db.relationship(
        'UserRecipe',
        back_populates='recipe',
        overlaps="users"
    )
    users = db.relationship(
        'User',
        secondary='user_recipe',
        back_populates='recipes',
        overlaps="users_association,recipe"
    )
    anonymous_users_association = db.relationship(
        'AnonymousUserRecipe',
        back_populates='recipe',
        overlaps="anonymous_users"
    )
    anonymous_users = db.relationship(
        'AnonymousUser',
        secondary='anonymous_user_recipe',
        back_populates='recipes',
        overlaps="anonymous_users_association,recipe"
    )

    ingredients = db.relationship('Ingredient', back_populates='recipe', lazy=True)
    processes = db.relationship('Process', backref='recipe', lazy=True)


class Ingredient(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(20), nullable=True)

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipe', back_populates='ingredients')
    nutrition = db.relationship('Nutrition', back_populates='ingredient', cascade="all, delete-orphan")


class Nutrition(db.Model):
    __tablename__ = 'nutrition'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10), nullable=True)

    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    ingredient = db.relationship('Ingredient', back_populates='nutrition')


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