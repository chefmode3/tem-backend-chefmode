web: gunicorn --bind 0.0.0.0:5000 --timeout 120 manage:app
worker: celery -A app.extensions.celery worker --loglevel=info
migrate: python manage.py db upgrade
