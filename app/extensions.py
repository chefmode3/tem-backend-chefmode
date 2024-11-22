import os
import ssl

from flask_mailman import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from celery import Celery
from flask_login import LoginManager
from flask_celeryext import FlaskCeleryExt

from app.celery_utils import make_celery


class Base(DeclarativeBase):
    pass

# ext_celery = FlaskCeleryExt(create_celery_app=make_celery)  # new



db = SQLAlchemy(model_class=Base)
migrate = Migrate()
mail = Mail()
# celery = create_celery()
login_manager = LoginManager()
