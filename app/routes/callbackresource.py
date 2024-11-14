import json

import requests
from flask import session,  redirect, request
from flask_restx import Resource
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests

from app.config import flow, GOOGLE_CLIENT_ID


class CallbackResource(Resource):
    def get(self):
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
