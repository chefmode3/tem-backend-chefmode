from __future__ import annotations

from datetime import datetime

from marshmallow import fields
from marshmallow import pre_load
from marshmallow import Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app.models import Recipe


class TaskIdSchema(Schema):
    task_id = fields.String(required=True)


class LinkRecipeSchema(Schema):
    link = fields.Str(required=True)


class RecipeSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = Recipe
        include_relationships = True
        load_instance = True
        exclude = ('nutritions',)

    created_at = fields.DateTime(dump_only=True)  # Ensure correct serialization format

    @pre_load
    def parse_dates(self, data, **kwargs):
        # Convert string dates to datetime objects if necessary
        for field in ['created_at', 'updated_at']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        return data


class RecipeSchemaSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = Recipe
        include_relationships = True
        load_instance = True
