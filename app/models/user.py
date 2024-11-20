from flask_login import UserMixin

from app.extensions import db
from datetime import datetime


class UserRecipe(db.Model):
    __tablename__ = 'user_recipe'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True)
    flag = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', back_populates='recipes_association')
    recipe = db.relationship('Recipe', back_populates='users_association')


class AnonymousUserRecipe(db.Model):
    __tablename__ = 'anonymous_user_recipe'

    anonymous_user_id = db.Column(db.Integer, db.ForeignKey('anonymous_user.id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True)
    flag = db.Column(db.Boolean, default=False)
    anonymous_user = db.relationship('AnonymousUser', back_populates='recipes_association')
    recipe = db.relationship('Recipe', back_populates='anonymous_users_association')


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    username = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    activate = db.Column(db.Boolean, default=False)
    google_token = db.Column(db.String(255), unique=True, nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    recipes_association = db.relationship('UserRecipe', back_populates='user')


    def __repr__(self):
        return f'<User {self.name}>'

    def __init__(self, name, email, activate=False, password=None, google_token=None, google_id=None):
        self.name = name
        self.email = email
        self.password = password
        self.activate = activate
        self.google_id = google_id
        self.google_token = google_token
        
