import os

from flask_login import login_required
from flask_restx import Namespace, Resource
from flask import request, abort, render_template, session
from marshmallow import ValidationError

from app.utils.send_email import verify_reset_token, activation_or_reset_email
from app.task.send_email import send_reset_email
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.services.user_service import UserService
from app.serializers.user_serializer import (
    UserSignupSchema,
    UserLoginSchema,
    UserResponseSchema,
    PasswordResetRequestSchema,
    ResetPasswordSchema, UserActivationSchema
)


auth_ns = Namespace('auth', description="user authentication")

signup_schema = UserSignupSchema()
signup_model = convert_marshmallow_to_restx_model(auth_ns, signup_schema)

user_activation_schema = UserActivationSchema()
user_activation_model = convert_marshmallow_to_restx_model(auth_ns, user_activation_schema)

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
    @auth_ns.response(201, "User successfully created")
    @auth_ns.response(400, "Validation Error")
    def post(self):
        try:
            # Validate and deserialize input
            data = signup_schema.load(request.get_json())
            user_data, is_activate = UserService.signup(data['email'], data['password'])
            # print(user_data)
            if is_activate:
                return user_response_schema.dump(user_data), 200
            elif not user_data:
                return {"error" "user not found"}, 404
            email = user_data.get("email")
            name = user_data.get("name")
            subject = "Email Activation"
            # email, body, subject, recipient
            url_frontend = "http://127.0.0.1:5000/auth/reset_password/"
            to = os.getenv('DEFAULT_FROM_EMAIL')
            # Render the HTML template with context
            template = 'welcome_email.html'
            body = render_template(template, name=name)
            send_reset_email.delay(email=email,  body=body, subject=subject, recipient=to)
            return activation_or_reset_email(email, name=name, subject=subject, template='confirm_email.html',
                                             url_frontend=url_frontend)
        except ValidationError as err:
            return {"errors": err.messages}, 400


@auth_ns.route('/signup/activation')
class SignupConfirmResource(Resource):
    @auth_ns.expect(user_activation_model)
    @auth_ns.response(201, "User Account successfully activated", model=user_activation_model)
    @auth_ns.response(400, "Validation Error")
    def post(self, token):
        try:
            # Validate and deserialize input
            data = user_activation_schema.load(request.get_json())
            email = data.get('email')
            result = verify_reset_token(token, max_age=86400)
            if not result["valid"]:
                return {"error": result["error"]}, 400
            return UserService.activate_user(email)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        except Exception as err:
            return {"errors": err}, 500


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
            data = password_reset_request_schema.load(request.get_json())
            email = data.get("email")
            url_frontend = " http://127.0.0.1:5000/auth/reset_password/"

            subject = "Password Reset Request"

            user = UserService.get_user_by_email(email)
            name: str = user.get('name')

            return activation_or_reset_email(email, name=name, subject=subject,  template='password_reset_email.html',
                                             url_frontend=url_frontend)

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

            data = reset_password_schema.load(request.get_json())
            email = data.get("email")
            new_password = data.get("new_password")
            token = data.get('token')
            result = verify_reset_token(token)
            if not result["valid"]:
                return {"error": result["error"]}, 400

            return UserService.reset_password(email, token, new_password)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        except Exception as err:
            return {"errors": err}, 500