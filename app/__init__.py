from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_cors import CORS
from app.extensions import db, migrate
from app.config import DevelopmentConfig
from app import cli
from app.routes.main_routes import auth_ns


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)

    app.config.from_object(config_class)
    api = Api(app, version='1.0', title='API', description='API documentation')
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)
    # Enable CORS
    CORS(app)

    url_api = '/api/v1'
    # Register blueprints
    from app.routes.logout_routes import LogoutResource
    from app.routes import LoginResource
    from app.routes import ProtectedAreaResource
    from app.routes import CallbackResource
    from app.routes import (
        SignupResource,
        LoginResource,
        LogoutResource,
        PasswordResetRequestResource,
        ResetPasswordResource,

    )
    api.add_namespace(auth_ns, path="/auth")




    cli.register(app)

    return app
