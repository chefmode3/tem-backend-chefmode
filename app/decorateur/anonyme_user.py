from __future__ import annotations

import logging
from functools import wraps

from flask import g
from flask import jsonify
from flask import make_response
from flask import request

from app.services import AnonymeUserService


Logger = logging.getLogger(__name__)


def load_or_create_anonymous_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Check if the user is logged in
            if g.get('user', None):
                return f(*args, **kwargs)

            # Get the client UUID
            client_uuid = request.headers.get('X-Client-UUID')
            anonymous_user = None
            #  new_user_created = False
            Logger.error(f"anonyme user {client_uuid}")
            if client_uuid:
                # Try to fetch the anonymous user
                anonymous_user = AnonymeUserService.get_anonymous_user_by_id(client_uuid)
            Logger.error(f"anonyme user {anonymous_user}")
            if not anonymous_user:
                # Create a new anonymous user if not found
                anonymous_user = AnonymeUserService.create_anonymous_user()

            # Link the anonymous user to the global context
            g.user = anonymous_user

            # Call the decorated function
            response = f(*args, **kwargs)

            # Handle different response formats
            if isinstance(response, tuple) and len(response) == 2:
                # Handle (dict, status_code) format
                response_body, status_code = response
                response_obj = make_response(jsonify(response_body), status_code)
            elif isinstance(response, dict):
                # Handle plain dict format
                response_obj = make_response(jsonify(response), 200)
            else:
                # Assume it's already a Response object
                response_obj = response

            # Modify headers if a new user was created

            response_obj.headers['X-Client-UUID'] = anonymous_user.id
            response_obj.headers['Access-Control-Expose-Headers'] = 'X-Client-UUID'
            return response_obj
        except Exception as err:
            Logger.error(f"Error in load_or_create_anonymous_user: {str(err)}")
            return {'error': 'An unexpected error occurred'}, 400

    return decorated_function


def track_anonymous_requests(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Retrieve the user from the global context
            user = g.get('user', None)

            # Ensure the user exists and has a request_count attribute
            if not user:
                Logger.error('No user found in global context')
                return f(*args, **kwargs)

            # Ensure the user has a request_count
            if not hasattr(user, 'request_count') or user.request_count is None:
                Logger.error('User has no request_count attribute or it is None')
                return f(*args, **kwargs)

            # Increment the request count
            updated_user = AnonymeUserService.increment_request_count(user.id)
            Logger.info(f"Request count for user {user.id}: {updated_user.request_count}")

            # Check if the request limit is exceeded
            if updated_user.request_count >= 6:
                Logger.warning(f"Request limit reached for user {user.id}")
                return {'error': 'Maximum free requests reached. Please register.'}, 403

            return f(*args, **kwargs)

        except Exception as err:
            Logger.error(f"Error in track_anonymous_requests: {err}")
            return {'error': 'Internal server error'}, 400

    return decorated_function
