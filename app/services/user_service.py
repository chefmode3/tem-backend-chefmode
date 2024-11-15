from app.models.user import User
from app.extensions import db
from flask import jsonify, abort, url_for
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt
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
            abort(400, description="Email already exists.")

        user = User(email=email, username=email.split('@')[0])
        user.password = generate_password_hash(password)

        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=email)
        return {
            "id": user.user_id,
            "email": user.email,
            "username": user.username,
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
            abort(401, description="Invalid credentials.")

        access_token = create_access_token(identity=email)
        return {
            "id": user.user_id,
            "email": user.email,
            "username": user.username,
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
            abort(404, description="User not found.")
        return {
            "id": user.user_id,
            "email": user.email,
            "username": user.username
        }

    @staticmethod
    def request_password_reset(email):
        """Generates a password reset token and sends it via email."""
        user = User.query.filter_by(email=email).first()
        if not user:
            abort(404, description="User not found.")

        reset_token = secrets.token_urlsafe(16)
        user.reset_token = reset_token
        db.session.commit()

        # Send email (assuming Mail is configured and initialized in the app)
        msg = Message("Password Reset Request",
                      sender=os.getenv('MAIL_USERNAME', 'inforeply@gmail.com'),
                      recipients=[email])
        msg.body = (f"Click the link to reset your password: "
                    f"{url_for('auth_reset_password_resource', token=reset_token, _external=True)}")
        mail.send(msg)

        return {"message": "Password reset email sent"}

    @staticmethod
    def reset_password(token, new_password):
        """Resets the user's password if the token is valid."""
        user = User.query.filter_by(reset_token=token).first()
        if not user:
            abort(400, description="Invalid or expired reset token.")

        if len(new_password) < 8:
            abort(400, description="Password must be at least 8 characters.")

        user.password = generate_password_hash(new_password)
        user.reset_token = None
        db.session.commit()

        return {"message": "Password has been reset successfully"}

    @staticmethod
    def update_user(user_id, **kwargs):
        """Updates user profile information."""
        user = User.query.get(user_id)
        if not user:
            abort(404, description="User not found.")

        for key, value in kwargs.items():
            setattr(user, key, value)

        db.session.commit()
        return {
            "id": user.user_id,
            "email": user.email,
            "username": user.username,

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
    def get_current_user():
        """Returns information about the currently authenticated user."""
        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first()
        if not user:
            abort(404, description="User not found.")

        return {
            "id": user.user_id,
            "email": user.email,
            "username": user.username
        }
