from marshmallow import Schema, fields, validate, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from app.models.user import User
from app.extensions import db


class RecipeSchema(SQLAlchemyAutoSchema):

        class Meta:
            model = Recipe
            load_instance = True
            exclude = ('recipe_id', 'user_id')
            include_fk = True


class RecipeForm(schema.Schema):
    name = fields.Str(required=True)
    description = fields.List(required=True)
    ingredients = fields.Str(required=True)
    instructions = fields.Str(required=True)
    image = fields.Str(required=True)
    category = fields.Str(required=True)
    user_id = fields.Int(required=True)