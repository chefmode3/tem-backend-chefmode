# celery_worker.py
from app import create_app
from app.celery_utils import celery

app = create_app()
app.app_context().push()