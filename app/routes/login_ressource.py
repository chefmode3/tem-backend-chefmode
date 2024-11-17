from flask import session
import json
import requests
from flask import session,  redirect, request, abort
from flask_restx import Resource, Namespace
from google.oauth2 import id_token
from flask_jwt_extended import create_access_token
import google.auth.transport.requests
from marshmallow import ValidationError
from app.extensions import db
from app.config import flow, GOOGLE_CLIENT_ID
from app.config import flow
from app.services.user_service import UserService
from app.serializers.user_serializer import UserSchema, UserRegisterSchema
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model


auth_google_ns = Namespace('google', description="Opérations d'authentification")
user_response_schema = UserSchema()
user_response_model = convert_marshmallow_to_restx_model(auth_google_ns, user_response_schema)
user_register_schema = UserRegisterSchema()
user_register_model = convert_marshmallow_to_restx_model(auth_google_ns, user_register_schema)


@auth_google_ns.route('/Login')
class LoginResource(Resource):

    def get(self):
        authorization_url, state = flow.authorization_url()
        session["state"] = state
        return {'authorization_url': authorization_url}


@auth_google_ns.route('/Logout')
class LogoutResource(Resource):

    def get(self):
        session.clear()
        return {'message': 'Logged out successfully'}


@auth_google_ns.route('/Callback')
class CallbackResource(Resource):

    @auth_google_ns.expect(user_response_model)
    @auth_google_ns.response(200, "User logged in successfully", model=user_register_model)
    @auth_google_ns.response(400, "Validation Error")
    def post(self):
        
        try:
            data = request.json

            try:
                validated_data = UserRegisterSchema().load(data)
            except ValidationError as err:
                print(err.messages)
                abort(400, description=err.messages)

            # Extract user information
            id_token_str = validated_data.get('google_token')
            google_id = validated_data.get('google_id')
            name = validated_data.get('name')
            email = validated_data.get('email')

            # # Check if the user already exists in the database
            user = UserService.get_user_by_email(email)
            # print(user)
            if not user:
                user = UserService.create_user(name, email, google_id=google_id, google_token=id_token_str, activate=True)
            #
            # # Generate an access token
            access_token = create_access_token(identity=email)
            #
            # # Add the access token to the response
            user['access_token'] = access_token

            return user, 200

        except ValueError as e:
            print(e)
            return {'error': f'Failed to create user {e}'}, 401