web: gunicorn --bind 0.0.0.0:5000 manage:app
worker: celery -A tasks worker --loglevel=info
migrate: python manage.py db upgrade
