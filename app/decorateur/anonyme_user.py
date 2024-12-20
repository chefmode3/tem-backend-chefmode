from __future__ import annotations

import logging
from functools import wraps

from flask import jsonify, make_response, request, g
from app.services import AnonymeUserService


Logger = logging.getLogger(__name__)

def load_or_create_anonymous_user(f):
    """
    Decorator to load or create an anonymous user and include its information in the response headers.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Check if user is authenticated
            if request.headers.get('Authorization'):
                Logger.info("Authenticated user detected.")
                return f(*args, **kwargs)

            # Extract X-Client-UUID from request headers
            client_uuid = request.headers.get('X-Client-UUID')
            Logger.debug(f"Received X-Client-UUID: {client_uuid}")

            # Fetch or create anonymous user
            anonymous_user = None
            if client_uuid:
                anonymous_user = AnonymeUserService.get_anonymous_user_by_id(client_uuid.strip())

            if not anonymous_user:
                anonymous_user = AnonymeUserService.create_anonymous_user()
                Logger.info(f"New anonymous user created with ID: {anonymous_user.id}")
            else:
                Logger.debug(f"Loaded existing anonymous user with ID: {anonymous_user.id}")

            # Save anonymous user in Flask's global context
            g.user = anonymous_user

            # Call the original function
            response = f(*args, **kwargs)

            # Ensure response is valid
            if response is None:
                Logger.error("Decorated function returned None. Ensure it returns a valid Flask response.")
                return make_response(jsonify({'error': 'Invalid response from server'}), 500)

            # Handle response formats
            if isinstance(response, tuple) and len(response) == 2:
                response_body, status_code = response
                response_obj = make_response(jsonify(response_body), status_code)
            elif isinstance(response, dict):
                response_obj = make_response(jsonify(response), 200)
            elif isinstance(response, (str, bytes)):
                response_obj = make_response(response, 200)
            else:
                response_obj = response  # Assume it's already a Flask response object

            # Add custom headers
            response_obj.headers['X-Client-UUID'] = anonymous_user.id
            response_obj.headers['Access-Control-Expose-Headers'] = 'X-Client-UUID'
            return response_obj

        except Exception as err:
            Logger.error(f"Error in load_or_create_anonymous_user: {err}", exc_info=True)
            return make_response(jsonify({'error': 'An unexpected error occurred'}), 400)

    return decorated_function


def track_anonymous_requests(f):
    """
    Decorator to track requests made by an anonymous user and enforce request limits.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Check if user is authenticated
            if request.headers.get('Authorization'):
                Logger.info("Authenticated user detected.")
                return f(*args, **kwargs)

            # Ensure the user is set in the global context
            if not hasattr(g, 'user') or g.user is None:
                Logger.warning("No user found in the global context.")
                return f(*args, **kwargs)

            user = g.user

            # Increment request count for the user
            updated_user = AnonymeUserService.increment_request_count(user.id)
            g.user = updated_user  # Update the global context
            Logger.info(f"Request count for user {user.id}: {updated_user.request_count}")

            # Enforce request limit
            max_requests = 100000 # This value is temporal, it's suppose to be 6
            if updated_user.request_count >= max_requests:
                Logger.warning(f"Request limit reached for user {user.id}.")
                return make_response(
                    jsonify({'error': 'Maximum free requests reached. Please register to continue.'}),
                    403
                )

            return f(*args, **kwargs)

        except Exception as err:
            Logger.error(f"Error in track_anonymous_requests: {err}", exc_info=True)
            return make_response(jsonify({'error': 'An unexpected error occurred'}), 400)

    return decorated_function
