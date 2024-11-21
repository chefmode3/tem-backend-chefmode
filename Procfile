web: gunicorn --bind 0.0.0.0:5000 manage:app
worker: celery -A app.extensions.celery worker --loglevel=info
init: python manage.py db init
migrate: python manage.py db migrate
upgrade: python manage.py db upgrade
