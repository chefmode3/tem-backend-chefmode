from app.models import AnonymousUser
from app.extensions import db
from utils.common import logger


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
        """Retrieves an anonymous user by their ID."""
        if user_id is None:
            return None

        try:
            # Optional: Validate UUID format if needed
            import uuid
            uuid.UUID(str(user_id))

            anonymous_user = AnonymousUser.query.filter(AnonymousUser.id == str(user_id)).first()
            return anonymous_user
        except (ValueError, TypeError):
            # Log invalid UUID or handle appropriately
            logger.warning(f"Invalid UUID format: {user_id}")
            return None

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
            anonymous_user.request_count += 1
            db.session.commit()
        return anonymous_user

    @staticmethod
    def decrement_request_count(user_id):
        anonymous_user = AnonymousUser.query.get(user_id)
        if anonymous_user:
            anonymous_user.request_count -= 1
            db.session.commit()
        return anonymous_user

