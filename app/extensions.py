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

    # Updated configuration using lowercase keys
    celery.conf.update(
        broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        accept_content=['json'],  # Only allow JSON content
        task_serializer='json',  # Serialize tasks using JSON
        result_serializer='json',  # Serialize results using JSON
        redis_max_connections=20,  # Limit Redis connections (optional)
        broker_connection_retry_on_startup=True
    )
    print(celery.conf.redis_backend_use_ssl)
    print(celery.conf.result_backend)

    return celery


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
mail = Mail()
celery = create_celery()
login_manager = LoginManager()
