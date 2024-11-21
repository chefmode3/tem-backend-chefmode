import os
import ssl

from flask_mailman import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from celery import Celery
from flask_login import LoginManager


class Base(DeclarativeBase):
    pass


def create_celery():
    celery = Celery(__name__)
    celery.conf.broker = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
    celery.conf.backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
    if os.environ.get("DEBUG"):
        celery.broker_use_ssl = {
            'ssl_cert_reqs': ssl.CERT_NONE
        }  # True
        celery.redis_backend_use_ssl = {
            'ssl_cert_reqs': ssl.CERT_NONE
        }  # True
    else:
        celery.broker_use_ssl ={
            'ssl_cert_reqs': ssl.CERT_REQUIRED
        } # True
        celery.redis_backend_use_ssl = {
            'ssl_cert_reqs': ssl.CERT_REQUIRED
        } # True


    return celery


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
mail = Mail()
celery = create_celery()
login_manager = LoginManager()
