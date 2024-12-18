from flask import Flask, request, g, jsonify

from app import create_app
from app.services import UserService, AnonymeUserService
from app.utils.utils import get_current_user

app = create_app()

@app.before_request
def verify_user_connection():
    """
    Middleware to verify if the user is authenticated or anonymous.
    Sets the `g.user` for connected users or `g.anonymous_user` for anonymous ones.
    """
    try:
        # Check for Authorization token (e.g., JWT)
        if request.headers.get('Authorization'):
            user_email = UserService.decode_jwt_token(request.headers['Authorization'])
            user = UserService.get_user_by_email(user_email)
            g.user = user
            g.is_authenticated = True
            return  # User authenticated

        # Check for anonymous user
        client_uuid = request.headers.get('X-Client-UUID')
        if client_uuid:
            anonymous_user = AnonymeUserService.get_anonymous_user_by_id(client_uuid)
            if anonymous_user:
                g.anonymous_user = anonymous_user
                g.is_authenticated = False
                return
            else:
                # Create a new anonymous user if none exists
                new_anonymous_user = AnonymeUserService.create_anonymous_user(client_uuid)
                g.anonymous_user = new_anonymous_user
                g.is_authenticated = False
                return

        # Fallback for no Authorization and no Client UUID
        g.user = None
        g.anonymous_user = None
        g.is_authenticated = False
    except Exception as e:
        app.logger.error(f"Error verifying user connection: {e}")
        return jsonify({'error': 'Failed to authenticate user'}), 400


@app.after_request
def add_user_to_response_headers(response):
        """
        Adds user information (e.g., X-Client-UUID) to response headers.
        """
        user, is_authenticated = get_current_user()
        if user and not is_authenticated:

            response.headers['Access-Control-Expose-Headers'] = 'X-Client-UUID'
            response.headers['X-Client-UUID'] = user.id
        return response
