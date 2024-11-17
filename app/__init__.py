import os

from flask import Flask
from flask_jwt_extended import JWTManager
from app.extensions import mail
from flask_restx import Api
from flask_cors import CORS
from app.extensions import db, migrate
from app.config import DevelopmentConfig
from app import cli
from app.routes.main_routes import auth_ns
from app.routes.usecase_route import recipe_ns
from app.routes.login_ressource import auth_google_ns


def create_app(script_info=None):
    app = Flask(__name__)

    app_settings = os.getenv('APP_SETTINGS')

    app.config.from_object(app_settings)

    api = Api(app, version='1.0', title='API', description='API documentation')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Enable CORS
    CORS(app)
    mail.init_app(app)
    JWTManager(app)

    url_api = '/api/v1'

    # Register blueprints

    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(recipe_ns, path="/recipe")
    api.add_namespace(auth_google_ns, path="/google")

    cli.register(app)

    return app
