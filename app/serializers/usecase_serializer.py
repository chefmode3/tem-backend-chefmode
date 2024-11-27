from marshmallow import Schema, fields, validate


class RecipeRequestSchema(Schema):
    recipe_id = fields.Str(required=True)


class FlagRecipeResponseSchema(Schema):
    message = fields.Str()


class FlagStatusResponseSchema(Schema):
    flagged = fields.Bool()


class NutrientSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    quantity = fields.Float(required=True, validate=validate.Range(min=0))
    unit = fields.Str(required=True, validate=validate.Length(max=10))


class IngredientSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    quantity = fields.Float(required=True, validate=validate.Range(min=0))
    unit = fields.Str(required=True, validate=validate.Length(max=20))
    nutrition = fields.Nested(NutrientSchema, many=True)


class ProcessSchema(Schema):
    id = fields.Str(dump_only=True)
    step_number = fields.Int(required=True, validate=validate.Range(min=1))
    instructions = fields.Str(required=True, validate=validate.Length(min=1))


class RecipeResponseSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    origin = fields.Str(required=False, validate=validate.Length(min=1, max=255))
    servings = fields.Int(required=False, validate=validate.Range(min=1))
    flag = fields.Boolean(dump_only=True)
    preparation_time = fields.Int(required=False, validate=validate.Range(min=0))
    description = fields.Str(required=False, validate=validate.Length(min=1))
    image_url = fields.Str(required=False, validate=validate.URL())
    ingredients = fields.Nested(IngredientSchema, many=True)
    processes = fields.Nested(ProcessSchema, many=True)


class RecipeQuerySchema(Schema):
    page = fields.Int(required=False, missing=1, validate=validate.Range(min=1))
    page_size = fields.Int(required=False, missing=10, validate=validate.Range(min=1, max=100))
    search = fields.Str(required=True)


class IngredientIDSchema(Schema):
    """
    Schema for validating the ingredient_id parameter.
    """
    ingredient_id = fields.Str(required=True, validate=lambda x: x > 0, error_messages={
        "required": "ingredient_id is required",
        "invalid": "ingredient_id must be a positive integer"
    })


class NutritionItemSchema(Schema):
    name = fields.String(required=True)
    value = fields.Float(required=True)
    unit = fields.String(required=True)


class NutritionSchema(Schema):
    name = fields.Str(required=False)
    total_quantity = fields.Float(required=False)
    unit_serving = fields.Float(required=False)
    unit = fields.Str(required=False)

    class Meta:
        fields = ("name", "total_quantity", "unit_serving", "unit")