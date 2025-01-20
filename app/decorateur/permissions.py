import jwt
import os
from datetime import datetime
from flask import request, abort

from app.models.user import RevokedToken


def token_required(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            abort(401, 'Token is missing or invalid.')
        try:
            decoded = jwt.decode(token.split()[1], os.environ.get("SECRET_KEY"), algorithms=['HS256'])
            expiration_datetime = decoded.get("exp")
            if(expiration_datetime < datetime.now().timestamp()):
                abort(401, "Token has expired")
            revoked_token = RevokedToken.query.filter_by(jti=decoded.get("jti")).first()
            if revoked_token:
                abort(401, "This token has expired")
        except Exception as e:
            abort(401, "Token has expired")
        return f(*args, **kwargs)
    return wrapper
