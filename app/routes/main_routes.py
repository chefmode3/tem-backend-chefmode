from flask_login import login_required
from flask_restx import Namespace, Resource
from flask import request, abort, session
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError

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

    @login_required
    def post(self):
        session.clear()
        return {'message': 'Logged out successfully'}


@auth_ns.route('/password_reset_request')
class PasswordResetRequestResource(Resource):

    @auth_ns.expect(password_reset_request_model)
    @auth_ns.response(200, "Password reset email sent", model=password_reset_request_model)
    @auth_ns.response(400, "Validation Error")
    def post(self):
        try:
            data = request.get_json()
            email = data.get("email")
            return UserService.request_password_reset(email)
        except Exception as err:
            return {"errors": err}, 500



@auth_ns.route('/reset_password/<string:token>')
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