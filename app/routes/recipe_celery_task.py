from flask import session

from flask_restx import Resource


class get(Resource):

    def get(self):
        print()
        return {'message': f"Hello {session['name']}!"}
