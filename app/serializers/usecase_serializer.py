from marshmallow import Schema, fields, validate


class RecipeRequestSchema(Schema):
    recipe_id = fields.Int(required=True)

class FlagRecipeResponseSchema(Schema):
    message = fields.Str()

class FlagStatusResponseSchema(Schema):
    flagged = fields.Bool()


class IngredientSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True,validate=validate.Length(min=1, max=100))
    quantity = fields.Float(required=False,validate=validate.Range(min=0))
    unit = fields.Str(required=False,validate=validate.Length(max=20))


class ProcessSchema(Schema):
    id = fields.Int(dump_only=True)
    step_number = fields.Int(required=True, validate=validate.Range(min=1))
    instructions = fields.Str(required=True,validate=validate.Length(min=1))


class RecipeResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    origin = fields.Str(required=True)
    servings = fields.Int()
    flag = fields.Boolean()
    preparation_time = fields.Int()
    description = fields.Str()
    image_url = fields.Str()
    ingredients = fields.Nested("IngredientSchema", many=True)
    processes = fields.Nested("ProcessSchema", many=True)


class RecipeQuerySchema(Schema):
    page = fields.Int(required=False, missing=1, validate=validate.Range(min=1))
    page_size = fields.Int(required=False, missing=10, validate=validate.Range(min=1, max=100))
    search = fields.Str(required=True)