import os
from datetime import timedelta

from dotenv import load_dotenv
from utils.settings import BASE_DIR

from google_auth_oauthlib.flow import Flow


load_dotenv()

CLIENT_SECRET_FILE = BASE_DIR / "client_secret.json"
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
flow = Flow.from_client_secrets_file(
    client_secrets_file=CLIENT_SECRET_FILE,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', '')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    """Base configuration"""
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_TB_ENABLED = True
    CSRF_ENABLED = True

    # SMTP setup to reset password
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
    MAIL_USE_SLL = os.getenv('MAIL_USE_SLL')

    # Celery config
    CELERY_broker_url = os.getenv('CELERY_BROKER_URL')
    RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
    REDIS_MAX_CONNECTIONS = 10
    TASK_SERIALIZER = 'json'
    RESULT_SERIALIZER = 'json'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)


class DevelopmentConfig(Config):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL_DEV')
    FLASK_ADMIN_SWATCH = 'cerulean'
    DEBUG_TB_ENABLED = True
    DEBUG = True  # Activate debug mode in development environment
    OAUTHLIB_RELAX_TOKEN_SCOPE = True

    # Set OAUTHLIB_INSECURE_TRANSPORT to 1
    OAUTHLIB_INSECURE_TRANSPORT = "1"


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')


class ProductionConfig(Config):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL')
    DEBUG = False  # Deactivate debug mode in production environment
