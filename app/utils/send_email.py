import logging
import os

from flask import render_template
from itsdangerous import URLSafeTimedSerializer

from app.services import UserService
from app.task.send_email import send_reset_email

logger = logging.getLogger(__name__)


def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))
    return serializer.dumps(email, salt="password-reset-salt")


def verify_reset_token(token, max_age=3600):  # 30 minutes
    serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=max_age)
        return {"valid": True, "email": email}
    except Exception as e:

        return {"valid": False, "error": str(e)}


def activation_or_reset_email(
        email: str,
        name:str,
        subject: str,
        template: str='password_reset_email.html',
        url_frontend: str="http://127.0.0.1:5000/auth/reset_password/"
):
    reset_token = generate_reset_token(email)

    user_token = UserService.request_password_reset(email, reset_token)
    reset_url = f"{url_frontend}{user_token.reset_token}"

    name = name
    to = os.getenv('DEFAULT_FROM_EMAIL')
    # Render the HTML template with context
    body = render_template(template, name=name, reset_url=reset_url)
    send_reset_email.delay(email=email, body=body, subject=subject, recipient=to)
    logger.info("status: Email task sent to queue, 200")

