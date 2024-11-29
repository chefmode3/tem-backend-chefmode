from __future__ import annotations

import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api

from app import cli
from app.extensions import db
from app.extensions import login_manager
from app.extensions import mail
from app.extensions import migrate
from app.routes.get_recipe import recipe_ns as recipe_name_space
from app.routes.login_ressource import auth_google_ns
from app.routes.main_routes import auth_ns
from app.routes.subscription_route import subscription_ns
from app.routes.usecase_route import recipe_ns


# Define the security scheme
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter the token as "Bearer <your-token>"'
    }
}


def create_app(script_info=None):
    app = Flask(__name__)
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)
    api = Api(
        app,
        prefix='/api/v1',
        version='1.0',
        title='CHEFMODE API',
        description='API documentation',
        authorizations=authorizations,
        security='Bearer'
    )

    # Initialize db
    db.init_app(app)
    migrate.init_app(app, db)

    # Enable CORS
    CORS(app, expose_headers=['X-Client-UUID'])

    # Initialize mail extension
    mail.init_app(app)

    # Initialize JWT Manager
    jwt = JWTManager(app)

    # Initialize login manager
    login_manager.init_app(app)

    # Register blueprints
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(auth_google_ns, path='/auth')
    api.add_namespace(recipe_ns, path='/recipe')
    api.add_namespace(recipe_name_space, path='/recipe')
    api.add_namespace(subscription_ns, path="/payment")

    # cli
    cli.register(app)

    return app
