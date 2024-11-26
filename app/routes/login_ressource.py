import requests
from flask import session,   request, abort
from flask_restx import Resource, Namespace
from oauthlib.oauth2.rfc6749.errors import MissingCodeError
from marshmallow import ValidationError
from app.config import flow, GOOGLE_CLIENT_ID
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests

from app.serializers.user_serializer import GoogleCallBackSchema, UserRegisterSchema
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.services import UserService

auth_google_ns = Namespace('auth', description="Opérations d'authentification")
user_callback_schema = GoogleCallBackSchema()
user_callback_model = convert_marshmallow_to_restx_model(auth_google_ns, user_callback_schema)
user_register_schema = UserRegisterSchema()
user_register_model = convert_marshmallow_to_restx_model(auth_google_ns, user_register_schema)


@auth_google_ns.route('/login_google')
class LoginResource(Resource):

    def get(self):
        authorization_url, state = flow.authorization_url()
        session["state"] = state
        return {'authorization_url': authorization_url}


@auth_google_ns.route('/logout_google')
class LogoutResource(Resource):

    def get(self):
        session.clear()
        return {'message': 'Logged out successfully'}


@auth_google_ns.route('/callback')
class CallbackResource(Resource):

    @auth_google_ns.expect(user_callback_model)
    @auth_google_ns.response(200, "User logged in successfully", model=user_register_model)
    @auth_google_ns.response(400, "Validation Error")
    def post(self):
        
        try:
            data = request.json

            validated_data = GoogleCallBackSchema().load(data)
            authorization_code = validated_data.get('code')
            # Verify the token with Google
            print(authorization_code)

            flow.fetch_token(authorization_response=authorization_code)
            credentials = flow.credentials
            request_session = requests.session()
            cached_session = cachecontrol.CacheControl(request_session)
            token_request = google.auth.transport.requests.Request(session=cached_session)
            id_info = id_token.verify_oauth2_token(
                id_token=credentials._id_token,
                request=token_request,
                audience=GOOGLE_CLIENT_ID
            )

            user, status = UserService.create_user(
                        email=id_info.get("email"),
                        name=id_info.get("name"),
                        activate=id_info.get("email_verified"),
                        google_id=id_info.get("sub"),
                        google_token=credentials._id_token,
                        )
            user_data = user_register_schema.dump(user)
            return {'result': user_data}, 401

        except ValidationError as err:
            abort(400, description=err.messages)
        except MissingCodeError as google_err:
            return {'error': f'{google_err}'}, 400
        except ValueError as e:
            return {'error': f'Failed to create user {e}'}, 401
