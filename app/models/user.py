import uuid
from flask_login import UserMixin
from sqlalchemy import func

from app.extensions import db
from datetime import datetime


class UserRecipe(db.Model):
    __tablename__ = 'user_recipe'
    user_id = db.Column(db.String(512), db.ForeignKey('user.id'), primary_key=True)
    recipe_id = db.Column(db.String(512), db.ForeignKey('recipes.id'), primary_key=True)
    flag = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', back_populates='recipes_association')
    recipe = db.relationship('Recipe', back_populates='users_association')


class AnonymousUserRecipe(db.Model):
    __tablename__ = 'anonymous_user_recipe'

    anonymous_user_id = db.Column(db.String(512), db.ForeignKey('anonymous_user.id'), primary_key=True)
    recipe_id = db.Column(db.String(512), db.ForeignKey('recipes.id'), primary_key=True)
    flag = db.Column(db.Boolean, default=False)
    anonymous_user = db.relationship('AnonymousUser', back_populates='recipes_association')
    recipe = db.relationship('Recipe', back_populates='anonymous_users_association')


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.String(512), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(512), nullable=True)
    email = db.Column(db.String(512), unique=True, nullable=False)
    activate = db.Column(db.Boolean, default=False)
    google_token = db.Column(db.String(512), unique=True, nullable=True)
    google_id = db.Column(db.String(512), unique=True, nullable=True)
    password = db.Column(db.String(512), unique=True, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reset_token = db.Column(db.String(512), unique=True, nullable=True)
    # Relationships
    recipes_association = db.relationship('UserRecipe', back_populates='user')

    def __repr__(self):
        return f'<User {self.name}>'


class RevokedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(512), nullable=False, index=True)
    type = db.Column(db.String(512), nullable=False)

    user_id = db.Column(db.ForeignKey('user.id'),nullable=False)
    created_at = db.Column(db.DateTime,server_default=func.now(),nullable=False,)
