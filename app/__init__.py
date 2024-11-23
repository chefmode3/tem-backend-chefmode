import os

from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app import cli
from app.extensions import mail, login_manager
from app.extensions import db, migrate
from app.config import DevelopmentConfig
from app.routes.get_recipe import recipe_ns as recipe_name_space
from app.routes.main_routes import auth_ns
from app.routes.login_ressource import auth_google_ns
from app.routes.usecase_route import recipe_ns


def create_app(script_info=None):
    app = Flask(__name__)
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)
    api = Api(app, prefix='/api/v1', version='1.0', title='API', description='API documentation')

    # Initialize db
    db.init_app(app)
    migrate.init_app(app, db)

    # Enable CORS
    CORS(app)

    # Initialize mail extension
    mail.init_app(app)

    # Initialize JWT Manager
    JWTManager(app)

    # Initialize login manager
    login_manager.init_app(app)

    # Register blueprints
    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(auth_google_ns, path="/auth")
    api.add_namespace(recipe_ns, path="/recipe")
    api.add_namespace(recipe_name_space, path="/recipe")


    # cli
    cli.register(app)

    return app
