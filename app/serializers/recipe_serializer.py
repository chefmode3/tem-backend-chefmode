from marshmallow import Schema, fields, validate, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from app.models import Recipe

class TaskIdSchema(Schema):
    task_id = fields.String(required=True)


class LinkRecipeSchema(Schema):
    link = fields.Str(required=True)