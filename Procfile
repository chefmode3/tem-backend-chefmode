web: gunicorn --bind 0.0.0.0:5000 app:app
worker: celery -A tasks worker --loglevel=info
migrate: python manage.py db upgrade
