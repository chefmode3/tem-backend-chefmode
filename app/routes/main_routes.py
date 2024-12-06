from __future__ import annotations

import logging
import os
from datetime import datetime, timezone, timedelta

from flask import abort
from flask import request
from flask import jsonify
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_restx import Namespace
from flask_restx import Resource
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from app import db
from app.decorateur.permissions import token_required
from app.models.user import RevokedToken, User
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.services.user_service import UserService
from app.serializers.user_serializer import (
    UserSignupSchema,
    UserLoginSchema,
    UserResponseSchema,
    PasswordResetRequestSchema,
    ResetPasswordSchema,
    UserActivationSchema,
    UpdateUserSchema,
    DeleteUserSchema
)
from app.utils.send_email import activation_or_reset_email, verify_reset_token

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

delete_user_schema = DeleteUserSchema()


@auth_ns.route('/signup')
class SignupResource(Resource):
    @auth_ns.expect(signup_model)
    @auth_ns.response(201, 'User successfully created')
    @auth_ns.response(400, 'Validation Error')
    def post(self):
        try:
            data = signup_schema.load(request.get_json())
            user_data, is_activate = UserService.signup(data['email'], data['password'])
            logger.info(user_data)

            if is_activate:
                return {'result': 'Account created'}, 200
            if user_data.reset_token:
                return {"result": "An email has already send please"
                                  " check your email to verify your address"
                        }, 200
            email = user_data.email
            name = user_data.name
            subject = "Welcome to Chefmode!"
            url_frontend = os.getenv('VERIFY_EMAIL_URL')
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
        except HTTPException as http_err:
            logger.error(f'HTTP Exception: {http_err.description}')
            return {"error": http_err.description}, http_err.code
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
            token = data.get('token', None)
            result = verify_reset_token(token)
            logger.error(f'user reset :1')
            if not result["valid"]:
                return {"error": result["error"]}, 400

            logger.error(f'user reset :12')

            email = result["email"]

            if not email:
                return {"error": "Token does not match"}, 400
            logger.error(f'user reset :112')
            user, status = UserService.activate_user(email)
            user_data = user_response_schema.dump(user)

            access_token = create_access_token(
                identity=email,
                expires_delta=timedelta(days=1)
            )
            user_data['access_token'] = access_token

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


@auth_ns.route('/resend-email')
class EmailVerificationResource(Resource):
    @auth_ns.expect(password_reset_request_model)
    @auth_ns.response(200, 'Verification email sent')
    @auth_ns.response(400, 'Validation Error')
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')

            user = UserService.get_user_by_email(email)
            if not user:
                return {"error": "User does not exist."}, 400

            if user.activate:
                return {"result": "User account is already verified."}, 200

            name = user.name
            subject = "Chefmode: Email Activation"
            url_frontend = os.getenv('VERIFY_EMAIL_URL')
            template = 'welcome_email.html'

            activation_or_reset_email(
                email,
                name=name,
                subject=subject,
                template=template,
                url_frontend=url_frontend
            )
            return {"result": "Please check your email to verify your address."}
        except ValidationError as err:
            logger.error(f'{err.messages} : status, 400')
            return {"errors": err.messages}, 400
        except Exception as e:
            logger.error(f'{str(e)} : status, 400')
            return {"errors": "Unexpected error occurred"}, 400


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
            access_token = create_access_token(
                identity=user_data.email,
                expires_delta=timedelta(days=1)
            )
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
    @jwt_required(verify_type=False)
    @token_required
    def post(self):
        token = get_jwt()
        user = User.query.filter_by(email=token["sub"]).first()
        jti = token["jti"]
        ttype = token["type"]
        now = datetime.now(timezone.utc)
        db.session.add(RevokedToken(user_id=user.id, jti=jti, type=ttype, created_at=now))
        db.session.commit()
        return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")


@auth_ns.route('/password_reset_request')
class PasswordResetRequestResource(Resource):

    @auth_ns.expect(password_reset_request_model)
    @auth_ns.response(
        200, "Password reset email sent", model=password_reset_request_model
    )
    @auth_ns.response(400, "Validation Error")
    @token_required
    def post(self):
        try:
            data = password_reset_request_schema.load(request.get_json())
            email = data.get('email')
            url_frontend = os.getenv('RESET_PASSWORD_URL')

            subject = 'Chefmode: Reset Password'

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
            new_password = data.get('new_password')
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
    @token_required
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
            logger.error(f'{err.messages} : status, 400')
            return {"errors": err.messages}, 400
        except Exception as e:
            logger.error(f'Unexpected error: {str(e)} : status, 400')
            return {"errors": "Unexpected error occurred"}, 400


@auth_ns.route('/delete/<string:user_id>')
class DeleteUserResource(Resource):

    @auth_ns.response(200, "User successfully deleted")
    @auth_ns.response(404, "User not found")
    @auth_ns.response(400, "Validation Error")
    @token_required
    def delete(self, user_id):
        """Delete user information (except password)."""
        try:
            user = UserService.delete_user(user_id)
            if not user:
                return {"message": "User not found"}, 404

            return {"message": "User successfully deleted"}, 200
        except ValidationError as err:
            logger.error(f'{err.messages} : status, 400')
            return {"errors": err.messages}, 400
        except Exception as e:
            logger.error(f'Unexpected error: {str(e)} : status, 400')
            return {"errors": "Unexpected error occurred"}, 400
