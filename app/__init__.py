from flask import Flask
from app.extensions import db, migrate
from app.config import DevelopmentConfig
from app import cli


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.main_routes import main_bp
    app.register_blueprint(main_bp)

    cli.register(app)

    return app
