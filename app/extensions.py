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
    celery = Celery(
        __name__,
        broker=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
        backend=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
        broker_use_ssl={
            'ssl_cert_reqs': ssl.CERT_NONE
        },
        redis_backend_use_ssl={
            'ssl_cert_reqs': ssl.CERT_NONE
        }
    )


    return celery


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
mail = Mail()
celery = create_celery()
login_manager = LoginManager()
