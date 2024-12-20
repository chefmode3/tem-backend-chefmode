import re

from flask import request, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError

from app.services import UserService
from app.services.anonyme_user_service import AnonymeUserService


def with_app_context(task_function):
    def wrapper(*args, **kwargs):
        from app import create_app
        app = create_app()
        with app.app_context():
            return task_function(*args, **kwargs)
    return wrapper


def get_current_user():
    """
    Helper function to get the current user (authenticated or anonymous).
    Returns the user object and a flag indicating if the user is authenticated.
    """
    try:
        verify_jwt_in_request()
        user = get_jwt_identity()
        user = UserService.get_user_by_email(user)
        return user, True
    except NoAuthorizationError:
        pass
    except Exception:
        pass

    user = AnonymeUserService.get_anonymous_user_by_id(request.headers.get('X-Client-UUID'))
    if user:
        return user, False

    return None, False  # No user found


def replace_int_unit_serving(chaine, new_value):
    """
    find and replace the integer in the string by his new value.

    :param chaine: the string that containt the value to update.
    :param new_value: the new value to replace the old integer.
    :return: the update string.
    """
    # find the first integer in the string
    pattern = r'\d+'
    match = re.search(pattern, chaine)

    if match:
        # extract the integer find
        entier_trouve = match.group()
        # replace the old integer by his new value
        chaine_modifiee = chaine.replace(entier_trouve, str(new_value), 1)
        return chaine_modifiee
    else:
        return chaine  # return the original string if no integer is found

