import os

from flask import Flask
from flask_jwt_extended import JWTManager

from app.celery_utils import celery
from app.extensions import mail, login_manager
from flask_restx import Api
from flask_cors import CORS
from app.extensions import db, migrate
from app.config import DevelopmentConfig
from app import cli
from app.routes.get_recipe import recipe_ns as recipe_name_space
from app.routes.main_routes import auth_ns
from app.routes.login_ressource import auth_google_ns
from app.routes.usecase_route import recipe_ns


def create_app(script_info=None):
    app = Flask(__name__)
    if os.environ.get("DEBUG"):
        app_settings = os.getenv('DEV_APP_SETTINGS')
    else:
        app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)
    api = Api(app, version='1.0', prefix='/api/v1', title='API', description='API documentation')
    app.config['MAIL_SERVER'] = 'localhost'
    app.config['MAIL_PORT'] = 8025
    app.config['MAIL_USERNAME'] = None
    app.config['MAIL_PASSWORD'] = None
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    celery.conf.update(app.config)
    # celery.conf.update(app.config)
    # Enable CORS
    CORS(app)

    mail.init_app(app)
    JWTManager(app)
    login_manager.init_app(app)


    # Register blueprints
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db}

    api.add_namespace(auth_ns, path=f"/auth")
    api.add_namespace(auth_google_ns, path=f"/auth")
    api.add_namespace(recipe_ns, path=f"/recipe")
    api.add_namespace(recipe_name_space, path=f"/recipe")

    cli.register(app)

    return app
