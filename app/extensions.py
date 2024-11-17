import os
import ssl

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_mail import Mail
from celery import Celery


class Base(DeclarativeBase):
    pass


def create_celery():
    celery = Celery(__name__)
    celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
    celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
    celery.broker_use_ssl ={
        'ssl_cert_reqs': ssl.CERT_NONE
    } # True
    celery.redis_backend_use_ssl = {
        'ssl_cert_reqs': ssl.CERT_NONE
    } # True

    return celery


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
mail = Mail()
celery = create_celery()
