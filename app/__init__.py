from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from app.extensions import db, migrate
from app.config import DevelopmentConfig
from app import cli


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)

    app.config.from_object(config_class)
    api = Api(app, version='1.0', title='API', description='API documentation')
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Enable CORS
    CORS(app)

    url_api = '/api/v1'
    # Register blueprints
    from app.routes.logout_routes import LogoutResource
    from app.routes import LoginResource
    from app.routes import ProtectedAreaResource
    from app.routes import CallbackResource

    api.add_resource(LoginResource, f'/login')
    api.add_resource(CallbackResource, f'/callback')
    api.add_resource(LogoutResource, f'/logout')
    api.add_resource(ProtectedAreaResource, f'/protected_area')

    cli.register(app)

    return app
