import os
import os
from os.path import join, dirname
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
# print(dotenv_path)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    """Base configuration"""
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_TB_ENABLED = False
    CSRF_ENABLED = True


# defining dev config
class DevelopmentConfig(Config):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL_DEV')
    FLASK_ADMIN_SWATCH = 'cerulean'
    DEBUG_TB_ENABLED = True


# defining testing config
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')


# defining production config
class ProductionConfig(Config):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
