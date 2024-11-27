import logging
import os

from flask_jwt_extended import create_access_token
from flask_login import login_required
from flask_restx import Namespace, Resource
from flask import request, abort, session
from marshmallow import ValidationError

from app.utils.send_email import verify_reset_token, activation_or_reset_email
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.services.user_service import UserService
from app.serializers.user_serializer import (
    UserSignupSchema,
    UserLoginSchema,
    UserResponseSchema,
    PasswordResetRequestSchema,
    ResetPasswordSchema,
    UserActivationSchema,
    UpdateUserSchema
)

logger = logging.getLogger(__name__)

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
password_reset_request_model = convert_marshmallow_to_restx_model(
    auth_ns, password_reset_request_schema
)

reset_password_schema = ResetPasswordSchema()
reset_password_model = convert_marshmallow_to_restx_model(auth_ns, reset_password_schema)

update_user_schema = UpdateUserSchema()
update_user_model = convert_marshmallow_to_restx_model(auth_ns, update_user_schema)


@auth_ns.route('/signup')
class SignupResource(Resource):
    @auth_ns.expect(signup_model)
    @auth_ns.response(201, "User successfully created")
    @auth_ns.response(400, "Validation Error")
    def post(self):
        try:
            data = signup_schema.load(request.get_json())
            user_data, is_activate = UserService.signup(data['email'], data['password'])
            logger.info(user_data)

            if is_activate:
                return {"result": "Account created"}, 200
            if user_data.reset_token:
                return {"result": "An email has already send please"
                                  " check your email to verify your address"
                        }, 200
            email = user_data.email
            name = user_data.name
            subject = "Email Activation"
            url_frontend = os.getenv('URL_FRONTEND')
            template = 'welcome_email.html'

            activation_or_reset_email(
                email,
                name=name,
                subject=subject,
                template=template,
                url_frontend=url_frontend
            )
            return {"result": "Your account has been created. "
                              "Please check your email to verify your address."
                    }, 200
        except ValidationError as err:
            logger.error(f'{err.messages} : status ,400')
            return {"errors": err.messages}, 400
        except Exception as inter_erro:
            logger.error(f'{str(inter_erro)} : status, 400')
            return {"errors": " unexpected error occurred"}, 400


@auth_ns.route('/signup/activation')
class SignupConfirmResource(Resource):
    @auth_ns.expect(user_activation_model)
    @auth_ns.response(
        201, "User Account successfully activated", model=user_activation_model
    )
    @auth_ns.response(400, "Validation Error")
    def post(self):
        try:
            data = user_activation_schema.load(request.get_json())
            email = data.get('email')
            token = data.get('token')

            result = verify_reset_token(token)
            logger.error(f'user reset :1')
            if not result["valid"]:
                return {"error": result["error"]}, 400

            logger.error(f'user reset :12')
            if result["email"] != email:
                return {"error": "Token does not match the provided email"}, 400
            logger.error(f'user reset :112')
            user, status = UserService.activate_user(email)
            user_data = user_response_schema.dump(user)
            logger.error(f'user reset :1212 {user}')
            if user:
                logger.error(f'user reset : {user_data}')

                return user_data, status
            return {"error": f"Token or email are invalid "}, status
        except ValidationError as err:
            logger.error(f'{err.messages} : status,400')
            return {"errors": err.messages}, 400
        except Exception as err:
            logger.error(f'{str(err)} : status,400')
            return {"errors": " unexpected error occurred"}, 400


@auth_ns.route('/login')
class LoginResource(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(
        201, "User successfully logged", model=user_response_model
    )
    @auth_ns.response(400, "Validation Error")
    def post(self):
        try:

            data = login_schema.load(request.get_json())
            user_data = UserService.login(data['email'], data['password'])
            access_token = create_access_token(identity=user_data.email)
            if user_data:
                user = user_response_schema.dump(user_data)
                user['access_token'] = access_token
                return user, 200
            else:
                abort(401, description="Invalid credentials.")
        except ValidationError as err:
            logger.error(f'{err.messages} : status ,400')
            return {"errors": err.messages}, 400

        except Exception as inter_erro:
            logger.error(f'{str(inter_erro)} : status ,400')
            return {"errors": " unexpected error occurred"}, 400


@auth_ns.route('/logout')
class LogoutResource(Resource):

    @login_required
    def post(self):
        session.clear()
        return {'message': 'Logged out successfully'}


@auth_ns.route('/password_reset_request')
class PasswordResetRequestResource(Resource):

    @auth_ns.expect(password_reset_request_model)
    @auth_ns.response(
        200, "Password reset email sent", model=password_reset_request_model
    )
    @auth_ns.response(400, "Validation Error")
    def post(self):
        try:
            data = password_reset_request_schema.load(request.get_json())
            email = data.get("email")
            url_frontend = os.getenv('REQUEST_PASSWORD')

            subject = "Password Reset Request"

            user = UserService.get_user_by_email(email)
            if not user:
                return {"result": "Email not found or incorrect"}

            name: str = user.name
            activation_or_reset_email(
                email,
                name=name,
                subject=subject,
                template='password_reset_email.html',
                url_frontend=url_frontend
            )
            return {"result": "An email is already sent to you "}

        except ValidationError as err:
            logger.error(f'{str(err)} : status, 400')
            return {"errors": err.messages}, 400

        except Exception as err:
            logger.error(f'{str(err)} : status, 400')
            return {"errors": " unexpected error occurred"}, 400


@auth_ns.route('/reset_password')
class ResetPasswordResource(Resource):

    @auth_ns.expect(reset_password_model)
    @auth_ns.response(
        200, "Password has been reset successfully", model=reset_password_model
    )
    @auth_ns.response(400, "Validation Error")
    def post(self):
        try:

            data = reset_password_schema.load(request.get_json())
            new_password = data.get("new_password")
            token = data.get('token')

            return UserService.reset_password(token, new_password)
        except ValidationError as err:
            logger.error(f'{err.messages} : status ,400')
            return {"errors": err.messages}, 400
        except Exception as inter_erro:
            logger.error(f'{str(inter_erro)} : status ,400')
            return {"errors": " unexpected error occurred"}, 400


@auth_ns.route('/user/<string:id>')
class UpdateUserResource(Resource):

    @auth_ns.expect(update_user_model)
    @auth_ns.response(200, "User updated successfully")
    @auth_ns.response(404, "User not found")
    @auth_ns.response(400, "Validation Error")
    def put(self, id):
        """Update user information (except password)."""
        try:
            data = update_user_schema.load(request.get_json())
            user = UserService.update_user(id, **data)
            if not user:
                return {"message": "User not found"}, 404

            return {"message": "User updated successfully",
                    "user": user_response_schema.dump(user)
                    }, 200
        except ValidationError as err:
            logger.error(f'{err.messages} : status 400')
            return {"errors": err.messages}, 400
        except Exception as e:
            logger.error(f'Unexpected error: {str(e)} : status, 400')
            return {"errors": "Unexpected error occurred"}, 400
