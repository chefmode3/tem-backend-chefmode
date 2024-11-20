from flask_restx import Namespace, Resource
from flask import request
from flask_login import login_required
from marshmallow import ValidationError


from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.services.usecase_logic import RecipeService
from app.serializers.usecase_serializer import (
    RecipeResponseSchema,
    RecipeRequestSchema,
    FlagStatusResponseSchema,
    RecipeQuerySchema,
    NutrientSchema,
    IngredientIDSchema
)
from app.services.user_service import UserService
from app.serializers.recipe_serializer import RecipeSerializer


recipe_ns = Namespace('recipe', description="user recipe")

# Schemas and models
recipe_response_schema = RecipeResponseSchema()
recipe_response_model = convert_marshmallow_to_restx_model(recipe_ns, recipe_response_schema)
recipe_ns.models[recipe_response_model.name] = recipe_response_model

flag_recipe_schema = RecipeRequestSchema()
flag_recipe_model = convert_marshmallow_to_restx_model(recipe_ns, flag_recipe_schema)

flag_status_schema = FlagStatusResponseSchema()
flag_status_model = convert_marshmallow_to_restx_model(recipe_ns, flag_status_schema)

recipe_query_schema = RecipeQuerySchema()

nutrition_response_model = convert_marshmallow_to_restx_model(recipe_ns, NutrientSchema())
nutrition_response_schema = IngredientIDSchema()


@recipe_ns.route('/get_recipe/<int:recipe_id>')
class GetRecipeResource(Resource):
    @recipe_ns.response(200, "Recipe fetched successfully", model=recipe_response_model)
    @recipe_ns.response(404, "Recipe not found")
    def get(self, recipe_id):
        """
        Fetch a single recipe by ID with its details.
        """
        try:
            recipe = RecipeService.get_recipe_by_id(recipe_id)
            return RecipeSerializer().dump(recipe), 200
        except Exception as e:
            return {"error": "An unexpected error occurred", "details": str(e)}, 500


@recipe_ns.route('/get_all_recipes')
class GetAllRecipesResource(Resource):
    @recipe_ns.doc(params={
        'page': 'Page number (default: 1)',
        'page_size': 'Number of results per page (default: 10)'
    })
    @recipe_ns.response(200, "Recipes fetched successfully", model=recipe_response_model)
    def get(self):
        """
        Fetch all recipes with pagination.
        """
        try:
            page = request.args.get("page", default=1, type=int)
            page_size = request.args.get("page_size", default=3, type=int)
            data = RecipeService.get_all_recipes(page, page_size)

            return {
                "data": RecipeSerializer(many=True).dump(data["data"]),
                "total": data["total"],
                "pages": data["pages"],
                "current_page": data["current_page"],
                "page_size": data["page_size"],
            }, 200
        except Exception as e:
            return {"error": "An unexpected error occurred", "details": str(e)}, 500


@recipe_ns.route('/get_my_recipes')
class GetMyRecipesResource(Resource):
    @login_required
    @recipe_ns.doc(params={
        'page': 'Page number (default: 1)',
        'page_size': 'Number of results per page (default: 10)'
    })
    @recipe_ns.response(200, "My recipes fetched successfully", model=recipe_response_model)
    def get(self):
        """
        Fetch recipes created by the logged-in user.
        """
        try:
            user = UserService.get_current_user()
            user_id = user['id']
            page = request.args.get("page", default=1, type=int)
            page_size = request.args.get("page_size", default=3, type=int)
            data = RecipeService.get_my_recipes(user_id, page, page_size)
            return {
                "data": RecipeSerializer(many=True).dump(data["data"]),
                "total": data["total"],
                "pages": data["pages"],
                "current_page": data["current_page"],
                "page_size": data["page_size"],
            }, 200
        except Exception as e:
            return {"error": "An unexpected error occurred", "details": str(e)}, 500


@recipe_ns.route('/flag_recipe')
class FlagRecipeResource(Resource):
    @login_required
    @recipe_ns.expect(flag_recipe_model)
    @recipe_ns.response(201, "Recipe flagged successfully.")
    def post(self):
        """
        Mark a recipe as flagged for the current user.
        """
        try:
            data = flag_recipe_schema.load(request.get_json())
            user = UserService.get_current_user()
            user_id = user['id']
            response = RecipeService.flag_recipe(data["recipe_id"], user_id)
            return response, 201
        except ValidationError as err:
            return {"errors": err.messages}, 400
        except Exception as e:
            return {"error": "An unexpected error occurred", "details": str(e)}, 500


@recipe_ns.route('/get_recipe/<int:recipe_id>/flag')
class IsRecipeFlaggedResource(Resource):
    @login_required
    @recipe_ns.response(200, "Flagged status fetched successfully.")
    def get(self, recipe_id):
        """
        Check if a recipe is flagged by the current user.
        """
        try:
            user = UserService.get_current_user()
            user_id = user['id']
            response = RecipeService.is_recipe_flagged_by_user(recipe_id, user_id)
            return flag_status_schema.dump(response), 200
        except Exception as e:
            return {"error": "An unexpected error occurred", "details": str(e)}, 500


@recipe_ns.route('/search')
class SearchRecipesResource(Resource):
    @recipe_ns.doc(params={
        'search': 'The search term to look for in recipes',
        'page': 'Page number (default: 1)',
        'page_size': 'Number of results per page (default: 10)'
    })
    @recipe_ns.response(200, "Search results fetched successfully.")
    @recipe_ns.response(400, "Validation Error")
    def get(self):
        """
        Search recipes by title.
        """
        try:
            search_term = request.args.get("search", default="", type=str)
            page = request.args.get("page", default=1, type=int)
            page_size = request.args.get("page_size", default=3, type=int)

            if not search_term:
                return {"message": "Search term is required."}, 400

            results = RecipeService.search_recipes(search_term, page, page_size)

            return {
                "data": RecipeSerializer(many=True).dump(results["data"]),
                "total": results["total"],
                "pages": results["pages"],
                "current_page": results["current_page"],
                "page_size": results["page_size"],
            }, 200
        except ValidationError as err:
            return {"errors": err.messages}, 400
        except Exception as e:
            return {"error": "An unexpected error occurred", "details": str(e)}, 500


@recipe_ns.route('/ingredient/<int:ingredient_id>/nutrition')
class IngredientNutritionResource(Resource):
    @recipe_ns.response(200, "Nutrition data fetched successfully.", model=nutrition_response_model)
    @recipe_ns.response(404, "Ingredient not found.")
    @recipe_ns.response(500, "Unexpected error.")
    def get(self, ingredient_id):
        """
        Get nutrition data for a specific ingredient.
        """
        try:
            nutrition_data = RecipeService.get_nutrition_by_ingredient(ingredient_id)
            if not nutrition_data:
                return {"message": "No nutrition data found for this ingredient."}, 200

            return RecipeSerializer().dump(nutrition_data), 200
        except ValueError as ve:
            return {"error": "Ingredient not found", "details": str(ve)}, 404
        except Exception as e:
            return {"error": "An unexpected error occurred", "details": str(e)}, 500
