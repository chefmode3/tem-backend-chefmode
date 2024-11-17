from app.models.user import User
from app.extensions import db
from flask import abort, url_for
from flask_jwt_extended import create_access_token, get_jwt_identity
import secrets
from app.extensions import mail
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
import os


class UserService:

    revoked_tokens = set()

    @staticmethod
    def signup(email, password):
        """Registers a new user."""
        if User.query.filter_by(email=email).first():
            return None
        user = User(email=email, name=email.split('@')[0])
        user.password = generate_password_hash(password)
        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=email)
        return {
            "id": user.user_id,
            "email": user.email,
            "name": user.username,
            "activate": user.activate,
            "google_token": "string",
            "google_id": "string",
            "access_token": access_token
        }

    @staticmethod
    def login(email, password):
        """Logs in a user if credentials are valid."""
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return None
        access_token = create_access_token(identity=email)
        return {
            "id": user.user_id,
            "email": user.email,
            "name": user.name,
            "access_token": access_token
        }

    def logout(self, jti):
        """Logs out a user by revoking their token."""
        self.revoked_tokens.add(jti)
        return {"message": "Successfully logged out"}

    @staticmethod
    def get_user_by_id(user_id):
        """Retrieves a user by their ID."""
        user = User.query.get(user_id)
        if not user:
            return None
        return {
            "id": user.user_id,
            "email": user.email,
            "name": user.name
        }

    @staticmethod
    def request_password_reset(email):
        """Generates a password reset token and sends it via email."""
        user = User.query.filter_by(email=email).first()
        if not user:
           return None
        reset_token = secrets.token_urlsafe(16)
        user.reset_token = reset_token
        db.session.commit()

        # Send email
        try:
            msg = Message(
                "Password Reset Request",
                sender=os.getenv('DEFAULT_FROM_EMAIL'),
                recipients=[email]
            )
            reset_url = url_for('auth_reset_password_resource', token=reset_token, _external=True)
            msg.body = (f"Hello,\n\n"
                        f"We received a request to reset your password. Click the link below to reset your password:\n"
                        f"{reset_url}\n\n"
                        f"If you didn't request this, you can ignore this email.")

            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {e}")
            return {"error": f"Error sending email: {e}"}

        return {"message": "Password reset email sent"}

    @staticmethod
    def reset_password(token, new_password):
        """Resets the user's password if the token is valid."""
        user = User.query.filter_by(reset_token=token).first()
        if not user:
           return None
        if len(new_password) < 8:
            return {"error": "password must be at least 8 characters"}

        user.password = generate_password_hash(new_password)
        user.reset_token = None
        db.session.commit()

        return {"message": "Password has been reset successfully"}

    @staticmethod
    def update_user(user_id, **kwargs):
        """Updates user profile information."""
        user = User.query.get(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            setattr(user, key, value)

        db.session.commit()
        return {
            "id": user.user_id,
            "email": user.email,
            "name": user.name,

        }

    @staticmethod
    def delete_user(user_id):
        """Deletes a user from the database."""
        user = User.query.get(user_id)
        if not user:
            return None

        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Changes the user's password if the old password is correct."""
        user = User.query.get(user_id)
        if not user or not check_password_hash(user.password, old_password):
            return None
        if len(new_password) < 8:
           return None

        user.password = generate_password_hash(new_password)
        db.session.commit()
        return {"message": "Password updated successfully"}

    @staticmethod
    def get_current_user():
        """Returns information about the currently authenticated user."""
        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return None

        return {
            "id": user.user_id,
            "email": user.email,
            "name": user.name
        }
