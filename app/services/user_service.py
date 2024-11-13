import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv


from flask import Flask, request, jsonify, redirect, url_for, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from flask_jwt_extended import create_access_token, JWTManager, get_jwt, jwt_required
from app.models import User
from app.extensions import db


load_dotenv()

app = Flask(__name__)

# SMTP setup to reset password
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

jwt = JWTManager(app)
mail = Mail(app)

class UserService:
    revoked_tokens = set()

    def signupEmail(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password or len(password) < 8:
            abort(
                400,
                description="Email and password are required,"
                            " with a password of min 8 characters."
            )

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists"}), 400

        username = email.split('@')[0]
        hashed_password = generate_password_hash(password)
        user = User(email=email, username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=email)
        return jsonify({
            "user_data": {"id": user.id, "email": user.email, "username": user.username},
            "access_token": access_token
        }), 201


    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    @staticmethod
    def loginEmail():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({"message": "Invalid credentials"}), 401

        access_token = create_access_token(identity=email)
        return jsonify({
            "user_data": {"id": user.id, "email": user.email, "username": user.username},
            "access_token": access_token
        }), 200


    @jwt_required()
    def logout(self):
        jti = get_jwt()["jti"]
        self.revoked_tokens.add(jti)
        return jsonify({"message": "Successfully logged out"}), 200
    

@jwt.token_in_blocklist_loader
def is_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in UserService.revoked_tokens


class PasswordService:

    @staticmethod
    def request_password_reset():
        data = request.get_json()
        email = data.get("email")

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"message": "Email not found"}), 404

        reset_token = secrets.token_urlsafe(16)
        user.reset_token = reset_token
        db.session.commit()

        msg = Message("Password Reset Request", sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = (f"Click the link to reset your password: "
                    f"{url_for('reset_password_token', token=reset_token, _external=True)}")
        mail.send(msg)
        return jsonify({"message": "Password reset email sent"}), 200

    @staticmethod
    def reset_password(token):
        data = request.get_json()
        new_password = data.get("new_password")

        user = User.query.filter_by(reset_token=token).first()
        if not user or len(new_password) < 8:
            return jsonify({"message": "Invalid token or weak password"}), 400

        user.password = generate_password_hash(new_password)
        user.reset_token = None
        db.session.commit()
        return jsonify({"message": "Password reset successful"}), 200