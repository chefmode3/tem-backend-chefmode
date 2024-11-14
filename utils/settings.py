from flask import session


import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return {'message': 'Authorization required'}, 401
        else:
            return function(*args, **kwargs)

    return wrapper