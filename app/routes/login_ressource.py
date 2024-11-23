
from flask import session,  redirect, request, abort
from flask_restx import Resource, Namespace
from oauthlib.oauth2.rfc6749.errors import MissingCodeError
from marshmallow import ValidationError
from app.config import flow

from app.serializers.user_serializer import GoogleCallBackSchema, UserRegisterSchema
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model


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
            try:
                validated_data = GoogleCallBackSchema().load(data)
            except ValidationError as err:
                abort(400, description=err.messages)
            authorization_code = validated_data.get('code')
            if not authorization_code:
                auth_google_ns.abort(400, f"Authorization {authorization_code} code is required")

            flow.fetch_token(authorization_response=authorization_code)
            # credentials = flow.credentials
            # request_session = requests.session()
            # cached_session = cachecontrol.CacheControl(request_session)
            # token_request = google.auth.transport.requests.Request(session=cached_session)
            # id_info = id_token.verify_oauth2_token(
            #     id_token=credentials._id_token,
            #     request=token_request,
            #     audience=GOOGLE_CLIENT_ID
            # )
            # print(id_info)
            # 
            # if user_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            #     raise ValueError('Wrong issuer.')
            # 
            # # Extract user information
            # id_token_str = user_info.get('google_token')
            # google_id = user_info.get('google_id')
            # name = user_info.get('name')
            # email = user_info.get('email')
            # 
            # # # Check if the user already exists in the database
            # user = UserService.get_user_by_email(email)
            # # print(user)
            # if not user:
            #     user = UserService.create_user(name, email, google_id=google_id, google_token=id_token_str, activate=True)
            # #
            # # # Generate an access token
            # access_token = create_access_token(identity=email)
            # #
            # # # Add the access token to the response
            # user['access_token'] = access_token
            # 
            # return user, 200
        except MissingCodeError as google_err:
            return {'error': f'{google_err}'}, 400
        except ValueError as e:
            return {'error': f'Failed to create user {e}'}, 401
