from flask import Flask
from app.extensions import db, migrate
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.main_routes import main_bp
    app.register_blueprint(main_bp)

    return app