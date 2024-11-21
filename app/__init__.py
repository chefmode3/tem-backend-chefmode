import os

from flask import Flask
from flask_jwt_extended import JWTManager
from app.extensions import mail, login_manager
from flask_restx import Api
from flask_cors import CORS
from app.extensions import db, migrate, celery
from app.config import DevelopmentConfig
from app import cli
from app.routes.get_recipe import recipe_ns as recipe_name_space
from app.routes.main_routes import auth_ns
from app.routes.login_ressource import auth_google_ns
from app.routes.usecase_route import recipe_ns


def create_app(script_info=None):
    app = Flask(__name__)
    if os.environ.get("DDEBUG"):
        app_settings = os.getenv('DEV_APP_SETTINGS')
    else:
        app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)
    api = Api(app, version='1.0', title='API', description='API documentation')
    app.config['MAIL_SERVER'] = 'localhost'
    app.config['MAIL_PORT'] = 8025
    app.config['MAIL_USERNAME'] = None
    app.config['MAIL_PASSWORD'] = None
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    class ContextTask(celery.Task):
        """Ajoute le contexte Flask aux tâches Celery."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    celery.conf.update(app.config)
    # Enable CORS
    CORS(app)

    mail.init_app(app)
    JWTManager(app)
    login_manager.init_app(app)

    url_api = '/api/v1'

    # Register blueprints

    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(auth_google_ns, path="/auth")
    api.add_namespace(recipe_ns, path="/recipe")
    api.add_namespace(recipe_name_space, path="/recipe")

    cli.register(app)

    return app
