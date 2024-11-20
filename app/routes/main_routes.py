import os

from flask_restx import Namespace, Resource
from flask import request, abort, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError
from app.task.send_email import send_reset_email
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.services.user_service import UserService
from app.serializers.user_serializer import (
    UserSignupSchema,
    UserLoginSchema,
    UserResponseSchema,
    PasswordResetRequestSchema,
    ResetPasswordSchema
)


auth_ns = Namespace('auth', description="user authentication")

signup_schema = UserSignupSchema()
signup_model = convert_marshmallow_to_restx_model(auth_ns, signup_schema)


login_schema = UserLoginSchema()
login_model = convert_marshmallow_to_restx_model(auth_ns, login_schema)

user_response_schema = UserResponseSchema()
user_response_model = convert_marshmallow_to_restx_model(auth_ns, user_response_schema)

password_reset_request_schema = PasswordResetRequestSchema()
password_reset_request_model = convert_marshmallow_to_restx_model(auth_ns, password_reset_request_schema)

reset_password_schema = ResetPasswordSchema()
reset_password_model = convert_marshmallow_to_restx_model(auth_ns, reset_password_schema)


@auth_ns.route('/signup')
class SignupResource(Resource):
    @auth_ns.expect(signup_model)
    @auth_ns.response(201, "User successfully created", model=user_response_model)
    @auth_ns.response(400, "Validation Error")
    def post(self):
        try:
            # Validate and deserialize input
            data = signup_schema.load(request.get_json())
            user_data = UserService.signup(data['email'], data['password'])
            if user_data:
                return user_response_schema.dump(user_data), 201
            else:
                abort(400, description="Email already exists.")
        except ValidationError as err:
            return {"errors": err.messages}, 400


@auth_ns.route('/signup/<string:token>')
class SignupConfirmResource(Resource):
    @auth_ns.response(201, "User Account successfully activated", model=user_response_model)
    @auth_ns.response(400, "Validation Error")
    def post(self, token):
        email = verification_tokens.get(token)
        if email:
            # Mark the user as verified
            users[email]['verified'] = True
            return user_response_schema.dump(users[email]), 201
        else:
            return {"error": "Invalid or expired verification token."}, 400


@auth_ns.route('/login')
class LoginResource(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(201, "User successfully logged", model=user_response_model)
    @auth_ns.response(400, "Validation Error")
    def post(self):
        try:
            # Validate and deserialize input
            data = login_schema.load(request.get_json())
            user_data = UserService.login(data['email'], data['password'])
            if user_data:
                return user_response_schema.dump(user_data), 200
            else:
                abort(401, description="Invalid credentials.")

        except ValidationError as err:
            return {"errors": err.messages}, 400


@auth_ns.route('/logout')
class LogoutResource(Resource):

    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        return UserService.logout(jti)


@auth_ns.route('/password_reset_request')
class PasswordResetRequestResource(Resource):

    @auth_ns.expect(password_reset_request_model)
    @auth_ns.response(200, "Password reset email sent", model=password_reset_request_model)
    @auth_ns.response(400, "Validation Error")
    def post(self):
        try:
            data = password_reset_request_schema.load(request.get_json())
            email = data.get("email")
            url_frontend = " http://127.0.0.1:5000/auth/reset_password/"
            user_token = UserService.request_password_reset(email)
            reset_url = f"{url_frontend}?email={email}&token={user_token.reset_token}"
            user = UserService.get_current_user()
            subject = "Password Reset Request"
            name = user.get('name')
            to = os.getenv('DEFAULT_FROM_EMAIL')
            # Render the HTML template with context
            body = render_template('password_reset_email.html', name=name, reset_url=reset_url)
            response = send_reset_email(email=email, body=body, subject=subject, recipient=to)
            # email, body, subject, recipient
            return response
        except ValidationError as err:
            return {"errors": err.messages}, 400

        except Exception as err:
            return {"errors": err}, 500



@auth_ns.route('/reset_password')
class ResetPasswordResource(Resource):

    @auth_ns.expect(reset_password_model)
    @auth_ns.response(200, "Password has been reset successfully", model=reset_password_model)
    @auth_ns.response(400, "Validation Error")
    def post(self, token):
        try:
            data = request.get_json()
            new_password = data.get("new_password")
            return UserService.reset_password(token, new_password)
        except Exception as err:
            return {"errors": err}, 500