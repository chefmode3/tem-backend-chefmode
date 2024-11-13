from flask import Blueprint, request
from app.services import UserService, PasswordService
from flask_jwt_extended import jwt_required


router = Blueprint("router", __name__)

user_service = UserService()
password_service = PasswordService()


@router.route('/signup', methods=['POST'])
def signup():
    return user_service.signupEmail()


@router.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return user_service.logout()


@router.route('/password-reset-request', methods=['POST'])
def password_reset_request():
    return password_service.request_password_reset()

@router.route('/password-reset/<token>', methods=['POST'])
def reset_password(token):
    return password_service.reset_password(token)
