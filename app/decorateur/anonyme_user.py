from flask import session, request, jsonify, g
from app.services import AnonymeUserService
from functools import wraps
import uuid

def load_or_create_anonymous_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # check if the user is login
        if g.get("user", None):
            return f(*args, **kwargs)

        # get the user id from the cleint
        client_uuid = request.headers.get("X-Client-UUID")
        anonymous_user = None
        if not client_uuid:
            # if not uuid is found then creat one
            anonymous_user = AnonymeUserService.create_anonymous_user()
        else:
            anonymous_user = AnonymeUserService.get_anonymous_user_by_id(client_uuid)

        # link anonyme user to the global context
        g.user = anonymous_user
        return f(*args, **kwargs)
    return decorated_function


def track_anonymous_requests(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = g.get("user", None)
        if not user or not user.is_anonymous:
            return f(*args, **kwargs)

        AnonymeUserService.increment_request_count(user.id)
        if user.request_count > 5:
            return jsonify({"error": "Maximum free requests reached. Please register."}), 403

        return f(*args, **kwargs)
    return decorated_function
