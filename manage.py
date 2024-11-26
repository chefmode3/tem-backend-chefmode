from flask.cli import FlaskGroup

from app import create_app
from app.extensions import make_celery

app = create_app()

cli = FlaskGroup(create_app=create_app)
celery = make_celery(app)

if __name__ == '__main__':
    cli()
