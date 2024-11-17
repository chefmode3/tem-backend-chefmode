from utils.settings import login_is_required
from flask import session

from flask_restx import Resource


class ProtectedAreaResource(Resource):
    @login_is_required
    def get(self):
        print()
        return {'message': f"Hello {session['name']}!"}
