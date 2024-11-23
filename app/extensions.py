import os

from flask_mailman import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from celery import Celery
from flask_login import LoginManager


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()


def make_celery(app):
    celery = Celery(__name__)

    # Updated configuration using lowercase keys
    celery.conf.update(
        broker_url=os.getenv('CELERY_broker_url'),
        result_backend=os.getenv('CELERY_RESULT_BACKEND'),
        accept_content=['json'],  # Only allow JSON content
        task_serializer='json',  # Serialize tasks using JSON
        result_serializer='json',  # Serialize results using JSON
        redis_max_connections=20,  # Limit Redis connections (optional)
        broker_connection_retry_on_startup=True
    )

    # Initialize Celery
    celery.conf.update(app.config)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():  # Push the application context
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
