from flask import request, abort


def token_required(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            abort(401, 'Token is missing or invalid.')
        # Validate the token here (e.g., decode JWT, check in a database)
        # Example:
        # decoded = jwt.decode(token.split()[1], SECRET_KEY, algorithms=['HS256'])
        return f(*args, **kwargs)
    return wrapper


def free_trail_recipe(fun):
    def wrapper(*args, **kwargs):
        return fun(*args, **kwargs)

    return wrapper
