web: gunicorn manage:app --timeout 9999999999
worker: celery -A manage.celery worker --loglevel=info
release: python manage.py db upgrade
