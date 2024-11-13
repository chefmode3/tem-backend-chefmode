from flask import session

from flask_restx import Resource
from app.config import flow


class LoginResource(Resource):

    def get(self):
        authorization_url, state = flow.authorization_url()
        session["state"] = state
        return {'authorization_url': authorization_url}
