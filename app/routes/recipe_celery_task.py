from flask import session

from flask_restx import Resource


class get(Resource):

    def get(self):
        return {'message': f"Hello {session['name']}!"}
