import os

from flask import render_template
from itsdangerous import URLSafeTimedSerializer

from app.services import UserService
from app.task.send_email import send_reset_email

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer("your_secret_key")
    return serializer.dumps(email, salt="password-reset-salt")

def verify_reset_token(token, max_age=3600):  # 30 minutes
    serializer = URLSafeTimedSerializer("your_secret_key")
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=max_age)
        return {"valid": True, "email": email}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def activation_or_reset_email(email: str, subject: str,  template: str='password_reset_email.html',url_frontend: str="http://127.0.0.1:5000/auth/reset_password/"):
    reset_token = generate_reset_token(email)

    user_token = UserService.request_password_reset(email, reset_token)
    reset_url = f"{url_frontend}?email={email}&token={user_token.reset_token}"
    user = UserService.get_current_user()
    name = user.get('name')
    to = os.getenv('DEFAULT_FROM_EMAIL')
    # Render the HTML template with context
    body = render_template(template, name=name, reset_url=reset_url)
    send_reset_email.delay(email=email, body=body, subject=subject, recipient=to)
    return {"status": "Email task sent to queue"}, 200
