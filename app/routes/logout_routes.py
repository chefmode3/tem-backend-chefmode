from flask import session

from flask_restx import Resource


class LogoutResource(Resource):
    def get(self):
        session.clear()
        return {'message': 'Logged out successfully'}
