import os
from os.path import join, dirname
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
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost:5000/callback"
)
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    """Base configuration"""
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_TB_ENABLED = True
    CSRF_ENABLED = True

    # SMTP setup to reset password

    MAIL_HOST = os.getenv('MAIL_HOST')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_BACKEND = os.getenv('MAIL_BACKEND')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
    MAIL_HOST_USER = os.getenv('MAIL_HOST_USER')
    MAIL_HOST_PASSWORD = os.getenv('MAIL_HOST_PASSWORD')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
    MAIL_USE_SLL = os.getenv('MAIL_USE_SLL')
    CELERY_broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    REDIS_MAX_CONNECTIONS = 10
    TASK_SERIALIZER = 'json'
    RESULT_SERIALIZER = 'json'
    ACCEPT_CONTENT = ['json']



# defining dev config
class DevelopmentConfig(Config):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
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
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    DEBUG = False  # Deactivate debug mode in production environment

