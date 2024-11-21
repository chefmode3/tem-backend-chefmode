web: gunicorn manage:app --timeout 9999999999
worker: celery -A app.extensions.celery worker --loglevel=info
init: python manage.py db init
migrate: python manage.py db migrate
upgrade: python manage.py db upgrade
