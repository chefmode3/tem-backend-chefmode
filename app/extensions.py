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
        broker="rediss://:p642ddb3ec97ce928365e89e184f912f75ba388a6f46660fd1a76f30c147e6318@ec2-52-2-51-43.compute-1.amazonaws.com:23299",
        backend="rediss://:p642ddb3ec97ce928365e89e184f912f75ba388a6f46660fd1a76f30c147e6318@ec2-52-2-51-43.compute-1.amazonaws.com:23299",
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
