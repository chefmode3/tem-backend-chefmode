from flask import request

from app.models import AnonymousUser
from app.extensions import db


class AnonymeUserService:

    revoked_tokens = set()

    @staticmethod
    def create_anonymous_user():
        anonymous_user = AnonymousUser(request_count=0)
        db.session.add(anonymous_user)
        db.session.commit()
        return anonymous_user

    @staticmethod
    def get_anonymous_user_by_id(user_id):
        """Retrieves a anonymous_user by their ID."""
        anonymous_user = AnonymousUser.query.get(user_id)
        # if not anonymous_user:
        #    return AnonymeUserService.create_anonymous_user()
        return anonymous_user

    @staticmethod
    def delete_user(user_id):
        """Deletes a anonymous_user from the database."""
        anonymous_user = AnonymousUser.query.get(user_id)
        if not anonymous_user:
           return False

        db.session.delete(anonymous_user)
        db.session.commit()
        return True

    @staticmethod
    def increment_request_count(user_id):
        anonymous_user = AnonymousUser.query.get(user_id)
        if anonymous_user:
            count = anonymous_user.request_count
            count += 1
            anonymous_user.request_count = count
            db.session.commit()
        return anonymous_user

    @staticmethod
    def decrease_request_count():
        user_id = request.headers.get('X-Client-UUID')
        anonymous_user = AnonymousUser.query.get(user_id)
        if anonymous_user:
            count = anonymous_user.request_count
            count -= 1
            anonymous_user.request_count = count
            db.session.commit()
        return anonymous_user
