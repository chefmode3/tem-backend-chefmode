import os
from dotenv import load_dotenv
from utils.settings import BASE_DIR

from google_auth_oauthlib.flow import Flow


dotenv_path = BASE_DIR / '.flaskenv'
load_dotenv(dotenv_path)

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
client_secrets_file = BASE_DIR / "client_secret.json"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    redirect_uri="http://localhost:5000/callback"
)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', "")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    """Base configuration"""
    TESTING = False
    CSRF_ENABLED = True


# defining dev config
class DevelopmentConfig(Config):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL_DEV')
    FLASK_ADMIN_SWATCH = 'cerulean'
    DEBUG_TB_ENABLED = True
    DEBUG = True  # Activate debug mode in development environment
    OAUTHLIB_RELAX_TOKEN_SCOPE = True

    # Set OAUTHLIB_INSECURE_TRANSPORT to 1
    OAUTHLIB_INSECURE_TRANSPORT = "1"


# defining testing config
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')


# defining production config
class ProductionConfig(Config):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    DEBUG = False  # Deactivate debug mode in production environment
