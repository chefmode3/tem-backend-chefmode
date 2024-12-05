import logging

from flask import abort
from flask_jwt_extended import get_jwt_identity
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.user import User
from app.extensions import db, login_manager

logger = logging.getLogger(__name__)


class UserService:

    revoked_tokens = set()

    @staticmethod
    def signup(email, password):
        """Registers a new user."""
        user = UserService.get_user_by_email(email)
        if user:
            abort(400, description="An account with this email already exists.")
        user = User(email=email, name=email.split('@')[0], activate=False)
        user.password = generate_password_hash(password)

        db.session.add(user)
        db.session.commit()

        return user, user.activate

    @staticmethod
    def login(email, password):
        """Logs in a user if credentials are valid."""
        user = UserService.get_user_by_email(email)
        if not user or not check_password_hash(user.password, password):
            abort(401, description="Invalid credentials.")
        if not user.activate:
            abort(401, description="user is not activate or delete")

        login_user(user)
        return user

    @staticmethod
    def create_user(name, email, password=None, google_id=None, google_token=None, activate=False):
        """Creates a new user."""
        if UserService.get_user_by_email(email):
            return None

        user = User(email=email, name=name,  google_id=google_id, google_token=google_token, activate=activate)
        if password:
            user.password = generate_password_hash(password)

        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_email(user_email):
        """Retrieves a user by their ID."""
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return None
        return user

    @staticmethod
    def get_user_by_id(user_id):
        """Retrieves a user by their ID."""
        user = User.query.get(id=user_id)
        if not user:
            return None
        return user

    @staticmethod
    def request_password_reset(email, reset_token) -> User | None:
        """Generates a password reset token and sends it via email."""
        user = UserService.get_user_by_email(email)
        if not user:
            return None

        user.reset_token = reset_token
        db.session.commit()
        # return User
        return user

    @staticmethod
    def reset_password(token: str, new_password: str):
        from app.utils.send_email import verify_reset_token
        """Resets the user's password if the token is valid."""

        result = verify_reset_token(token)
        if not result["valid"]:
            return {"error": result["error"]}, 400

        email = result["email"]
        user =UserService.get_user_by_email(email)
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
           return None

        for key, value in kwargs.items():
            setattr(user, key, value)

        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        """Deletes a user from the database."""
        user = User.query.get(user_id)
        if not user:
            return None
        user.deleted = True
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
        user_identity = get_jwt_identity()
        if not user_identity:
            return None
        user = User.query.filter_by(email=user_identity).first()
        if not user:
            return None
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }

    @classmethod
    def activate_user(cls, email):
        try:
            user = UserService.get_user_by_email(email)
            logger.error(f'user reset :{user.reset_token == None}')
            if not user or not user.reset_token:
                return None, 400
            user.activate = True
            user.reset_token = None
            db.session.add(user)
            db.session.commit()
            return user, 200

        except Exception as e:
            db.session.rollback()
            # Rollback si erreur
            return {"error": str(e)}, 400
