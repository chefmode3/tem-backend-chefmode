import logging

from flask_restx import Namespace, Resource
from flask import request
from flask_login import login_required
from marshmallow import ValidationError

from app.decorateur.permissions import token_required
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.services.usecase_logic import RecipeService
from app.serializers.usecase_serializer import (
    RecipeResponseSchema,
    RecipeRequestSchema,
    FlagStatusResponseSchema,
    NutritionSchema
)

from app.services.user_service import UserService
from app.serializers.recipe_serializer import RecipeSerializer

from app.decorateur.anonyme_user import track_anonymous_requests, load_or_create_anonymous_user

logger = logging.getLogger(__name__)

recipe_ns = Namespace('recipe', description="user recipe")

# Schemas and models
recipe_response_schema = RecipeResponseSchema()
recipe_response_model = convert_marshmallow_to_restx_model(recipe_ns, recipe_response_schema)
recipe_ns.models[recipe_response_model.name] = recipe_response_model

flag_recipe_schema = RecipeRequestSchema()
flag_recipe_model = convert_marshmallow_to_restx_model(recipe_ns, flag_recipe_schema)

flag_status_schema = FlagStatusResponseSchema()

nutrition_response_model = convert_marshmallow_to_restx_model(recipe_ns, NutritionSchema())

@recipe_ns.route('/get_recipe_by_id')
class GetRecipeResource(Resource):
    @track_anonymous_requests
    @load_or_create_anonymous_user
    @recipe_ns.doc(params={
        'recipe_id': {'description': 'The ID of the recipe to fetch',
                      'required': True,
                      'type': 'string'
                      },
        'serving': {'description': 'The serving size to adjust the recipe (optional)',
                    'required': False,
                    'type': 'integer'
                    }
    })
    @recipe_ns.response(
        200, "Recipe fetched successfully",model=recipe_response_model

    )
    @recipe_ns.response(404, "Recipe not found")
    def get(self):
        """
        Fetch a single recipe by ID with its details.
        """
        try:
            serving = request.args.get('serving', type=int)
            recipe_id = request.args.get('recipe_id', type=str)
            recipe = RecipeService.get_recipe_by_id(recipe_id, serving)
            return RecipeSerializer().dump(recipe), 200
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return {"error": "An unexpected error occurred", "details": str(e)}, 400


@recipe_ns.route('/get_all_recipes')
class GetAllRecipesResource(Resource):
    @track_anonymous_requests
    @load_or_create_anonymous_user
    @recipe_ns.doc(params={
        'page': 'Page number (default: 1)',
        'page_size': 'Number of results per page (default: 10)'
    })
    @recipe_ns.response(
        200, "Recipes fetched successfully", model=recipe_response_model
    )
    def get(self):
        """
        Fetch all recipes with pagination.
        """
        try:
            page = request.args.get("page", default=1, type=int)
            page_size = request.args.get("page_size", default=10, type=int)
            data = RecipeService.get_all_recipes(page, page_size)

            return {
                "data": RecipeSerializer(many=True).dump(data["data"]),
                "total": data["total"],
                "pages": data["pages"],
                "current_page": data["current_page"],
                "page_size": data["page_size"],
            }, 200
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return {"error": "An unexpected error occurred", "details": str(e)}, 400


@recipe_ns.route('/get_my_recipes')
class GetMyRecipesResource(Resource):
    @token_required
    @recipe_ns.doc(params={
        'page': 'Page number (default: 1)',
        'page_size': 'Number of results per page (default: 10)'
    })
    @recipe_ns.response(200,
                        "My recipes fetched successfully",
                        model=recipe_response_model
                        )
    def get(self):
        """
        Fetch recipes created by the logged-in user.
        """
        try:
            user = UserService.get_current_user()
            user_id = user['id']
            page = request.args.get("page", default=1, type=int)
            page_size = request.args.get("page_size", default=10, type=int)
            data = RecipeService.get_my_recipes(user_id, page, page_size)
            return {
                "data": RecipeSerializer(many=True).dump(data["data"]),
                "total": data["total"],
                "pages": data["pages"],
                "current_page": data["current_page"],
                "page_size": data["page_size"],
            }, 200
        except Exception as e:
            logger.error(f'An unexpected error occurred", "details": {str(e)}')
            return {"error": "An unexpected error occurred"}, 400


@recipe_ns.route('/flag_recipe')
class FlagRecipeResource(Resource):
    @token_required
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
            logger.error(f"Validation error occurred: {str(err)}")
            return {"errors": err.messages}, 400
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return {"error": "An unexpected error occurred", "details": str(e)}, 500


@recipe_ns.route('/get_recipe/<string:recipe_id>/flag')
class IsRecipeFlaggedResource(Resource):
    @token_required
    @recipe_ns.doc(params={
        'recipe_id': {'description': 'The ID of the recipe to fetch',
                      'required': True,
                      'type': 'string'}
    })
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
            logger.error(f"An unexpected error occurred: {str(e)}")
            return {"error": "An unexpected error occurred", "details": str(e)}, 400


@recipe_ns.route('/search')
class SearchRecipesResource(Resource):
    @token_required
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
            page_size = request.args.get("page_size", default=10, type=int)

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
            logger.error(f"Validation error occurred: {str(err)}")
            return {"errors": err.messages}, 400
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return {"error": "An unexpected error occurred", "details": str(e)}, 400


@recipe_ns.route('/nutrition_by_recipe_id')
class IngredientNutritionResource(Resource):
    @token_required
    @recipe_ns.doc(params={
        'recipe_id': {'description': 'The ID of the recipe to fetch',
                      'required': True,
                      'type': 'string'
                      },
        'serving': {'description': 'The serving size to adjust the recipe (optional)',
                    'required': False,
                    'type': 'integer'
                    }
    })
    @recipe_ns.response(200,
                        "Nutrition data fetched successfully.",
                        model=nutrition_response_model
                        )
    @recipe_ns.response(404, "Ingredient not found.")
    @recipe_ns.response(400, "Unexpected error.")
    def get(self):
        """
        Get nutrition data for a specific ingredient.
        """
        try:
            serving = request.args.get('serving', type=int)
            recipe_id = request.args.get('recipe_id', type=str)
            nutrition_service = RecipeService.get_nutrition_by_recipe_id(recipe_id, serving)

            if not nutrition_service:
                return {"message": "No nutrition data found for this ingredient."}, 200

            return NutritionSchema(many=True).dump(nutrition_service), 200

        except ValueError as ve:
            logger.error(f"An unexpected error occurred: {str(ve)}")
            return {"error": "Ingredient not found", "details": str(ve)}, 404
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return {"error": "An unexpected error occurred", "details": str(e)}, 400
