from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from flask import abort
from flask_jwt_extended import create_access_token

from app.models.user import User
from app.extensions import db, login_manager

from app.serializers.user_serializer import UserSchema


class UserService:

    revoked_tokens = set()

    @staticmethod
    def signup(email, password):
        """Registers a new user."""
        user = User.query.filter_by(email=email).first()
        if user and user.activate:
            abort(400, description="Email already exists."), False
        elif user and not user.activate:
            return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "activate": user.activate,

        }, False
        user = User(email=email, name=email.split('@')[0])
        user.password = generate_password_hash(password)

        db.session.add(user)
        db.session.commit()

        return {"success": "Your account has been created. Please check your email to verify your address."}, True

    @staticmethod
    def login(email, password):
        """Logs in a user if credentials are valid."""
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            abort(401, description="Invalid credentials.")
        if not user.activate:
            abort(401, description="user is not activate or delete")

        access_token = create_access_token(identity=email)
        login_user(user)
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "access_token": access_token
        }

    @staticmethod
    def create_user(name, email, password=None, google_id=None, google_token=None, activate=False):
        """Creates a new user."""
        if User.query.filter_by(email=email).first():
            abort(400, description="Email already exists.")

        user = User(email=email, name=name,  google_id=google_id, google_token=google_token, activate=activate)
        if password:
            user.password = generate_password_hash(password)

        db.session.add(user)
        db.session.commit()
        return UserSchema().dump(user)

    @staticmethod
    def get_user_by_email(user_email):
        """Retrieves a user by their ID."""
        print('----------------------------')
        user = User.query.filter_by(email=user_email).first()
        print('user', user.name)
        if not user:
            return None
        return UserSchema().dump(user)

    @staticmethod
    def get_user_by_id(user_id):
        """Retrieves a user by their ID."""
        user = User.query.get(id=user_id)
        if not user:
            abort(404, description="User not found.")
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }

    @staticmethod
    def request_password_reset(email, reset_token) -> User:
        """Generates a password reset token and sends it via email."""
        user = User.query.filter_by(email=email).first()
        if not user:
            abort(404, description="User not found.")

        user.reset_token = reset_token
        db.session.commit()
        # return User
        return user

    @staticmethod
    def reset_password(email: str, token: str, new_password: str):
        """Resets the user's password if the token is valid."""

        user = User.query.filter_by(reset_token=token, email=email).first()
        if not user:
            return {"error": "Invalid or expired reset token."}, 404

        if len(new_password) < 8:
            return {"error": "Password must be at least 8 characters."}, 400

        user.password = generate_password_hash(new_password)
        user.reset_token = None
        db.session.commit()

        return {"message": "Password  reset successfully"}


    @staticmethod
    def update_user(id, **kwargs):
        """Updates user profile information."""
        user = User.query.get(id)
        if not user:
            abort(404, description="User not found.")

        for key, value in kwargs.items():
            setattr(user, key, value)

        db.session.commit()
        return {
            "id": id,
            "email": user.email,
            "name": user.name,

        }

    @staticmethod
    def delete_user(user_id):
        """Deletes a user from the database."""
        user = User.query.get(user_id)
        if not user:
            abort(404, description="User not found.")

        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Changes the user's password if the old password is correct."""
        user = User.query.get(user_id)
        if not user or not check_password_hash(user.password, old_password):
            abort(400, description="Invalid old password.")

        if len(new_password) < 8:
            abort(400, description="Password must be at least 8 characters.")

        user.password = generate_password_hash(new_password)
        db.session.commit()
        return {"message": "Password updated successfully"}

    @staticmethod
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(str(user_id))

    @staticmethod
    def get_current_user():
        """Returns information about the currently authenticated user."""
        user = current_user
        if not user.is_authenticated:
            return None

        return {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }

    @classmethod
    def activate_user(cls, email):
        user = UserService.get_user_by_email(email)
        print('-----------------', user)
        if not user:
            return {"error": f"{email} not found"}, 400
        user.activate = True
        db.session.add(user)
        db.session.commit()
        return {"result": "user activate"}, 200
