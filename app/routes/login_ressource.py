from flask import session
import json
import requests
from flask import session,  redirect, request
from flask_restx import Resource, Namespace
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests
from app.config import flow, GOOGLE_CLIENT_ID
from app.config import flow


auth_google_ns = Namespace('auth', description="Opérations d'authentification")


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

    # @auth_google_ns.expect(password_reset_request_model)
    # @auth_google_ns.response(200, "Password reset email sent", model=password_reset_request_model)
    @auth_google_ns.response(400, "Validation Error")
    def post(self):
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        request_session = requests.session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)
        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID
        )

        google_id = id_info.get('sub')
        name = id_info.get('name')
        email = id_info.get('email')
        return redirect('https://www.google.com')
