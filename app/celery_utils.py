import os

from celery import Celery


def make_celery():
    celery = Celery(__name__)

    # Updated configuration using lowercase keys
    celery.conf.update(
        broker_url=os.getenv('CELERY_broker_url', 'redis://localhost:6379/0'),
        result_backend=os.getenv('result_backend', 'redis://localhost:6379/0'),
        accept_content=['json'],  # Only allow JSON content
        task_serializer='json',  # Serialize tasks using JSON
        result_serializer='json',  # Serialize results using JSON
        redis_max_connections=20,  # Limit Redis connections (optional)
        broker_connection_retry_on_startup=True
    )

    return celery


celery = make_celery()