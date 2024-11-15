from marshmallow import Schema, fields, validate, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from app.models.user import User
from app.extensions import db
