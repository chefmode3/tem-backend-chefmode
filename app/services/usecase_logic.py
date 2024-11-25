import logging
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.recipe import Recipe
from app.models.user import UserRecipe

logger = logging.getLogger(__name__)


class RecipeService:

    @staticmethod
    def get_recipe_by_id(recipe_id: str, serving: str=None):
        """
        Get a recipe with its ingredients and processes by ID.
        """
        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            return None
        if not serving:
            return recipe
        ingredient_pre_serving = []
        for ingredient in recipe.ingredients:
            quantity = ingredient.get("quantity")
            new_quantity = (serving * quantity) / recipe.servings
            ingredient_pre_serving.append({
                "name": ingredient["name"],
                "quantity": round(new_quantity, 2),
                "unit": ingredient["unit"]
            })
        recipe.ingredients = ingredient_pre_serving
        return recipe



    @staticmethod
    def get_all_recipes(page, page_size):
        """
        Get all recipes with pagination and related ingredients and processes.
        """
        query = Recipe.query.options(
            db.joinedload(Recipe.users_association)
        ).order_by(Recipe.created_at.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        return {
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
            "page_size": pagination.per_page,
            "data": [recipe for recipe in pagination.items]
        }

    @staticmethod
    def get_my_recipes(user_id, page, page_size):
        """
        Get recipes created by a specific user with pagination.
        """
        query = Recipe.query.join(UserRecipe).filter(
            UserRecipe.user_id == user_id
        ).order_by(Recipe.created_at.desc())

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        return {
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
            "page_size": pagination.per_page,
            "data": [
                {
                    "id": recipe.id,
                    "title": recipe.title,
                    "origin": recipe.origin,
                    "servings": recipe.servings,
                    "created_at": recipe.created_at,
                    "preparation_time": recipe.preparation_time,
                    "description": recipe.description,
                    "image_url": recipe.image_url,
                    "ingredients": recipe.ingredients,
                    "processes": recipe.processes,
                }
                for recipe in pagination.items
            ]
        }

    @staticmethod
    def flag_recipe(recipe_id, user_id):
        """
        Mark a recipe as flagged for a specific user.
        """
        user_recipe = UserRecipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()

        if not user_recipe:
            return None
        user_recipe.flag = not user_recipe.flag

        try:
            db.session.commit()
            return {
                "message": "Recipe flag status updated successfully.",
                "flag": user_recipe.flag
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error occurred: {str(e)}")
            return {"error": "Database error occurred", "details": str(e)}, 400

    @staticmethod
    def is_recipe_flagged_by_user(recipe_id, user_id):
        """
        Check if a recipe is flagged by the current user.
        """
        user_recipe = UserRecipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()

        if not user_recipe:
            return None

        return {"flagged": user_recipe.flag}

    @staticmethod
    def search_recipes(search_term, page=1, page_size=10):
        """
        Search for recipes by title with pagination.
        """
        try:
            query = Recipe.query.filter(
                Recipe.title.ilike(f"%{search_term}%")
            )

            pagination = query.paginate(page=page, per_page=page_size, error_out=False)

            return {
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": pagination.page,
                "page_size": pagination.per_page,
                "data": [
                    {
                        "id": recipe.id,
                        "title": recipe.title,
                        "origin": recipe.origin,
                        "servings": recipe.servings,
                        "created_at": recipe.created_at,
                        "preparation_time": recipe.preparation_time,
                        "description": recipe.description,
                        "image_url": recipe.image_url,
                        "ingredients": recipe.ingredients,
                        "processes": recipe.processes,
                    }
                    for recipe in pagination.items
                ]
            }
        except Exception as e:
            logger.error(f"Database error occurred: {str(e)}")
            return {"error": "Database error occurred", "details": str(e)}, 400

    @staticmethod
    def get_nutrition_by_recipe_id(recipe_id: str, serving: int):
        """
        Fetch nutrition data for a specific recipe.
        Optionally adjust nutrition quantities based on servings.
        :param recipe_id: ID of the recipe
        :param serving: New serving size (optional)
        :return: List of nutrients with adjusted quantities if serving is provided
        """
        try:
            recipe = Recipe.query.filter_by(id=recipe_id).first()
            if not recipe or not recipe.nutritions:
                return None

            adjusted_nutritions = []
            original_servings = recipe.servings

            for nutrition in recipe.nutritions:
                name = nutrition.get("name")
                original_total_quantity = nutrition.get("quantity")
                unit = nutrition.get("unit")

                if serving:
                    new_total_quantity = (serving * original_total_quantity) / original_servings
                    unit_quantity = new_total_quantity / serving
                else:
                    new_total_quantity = original_total_quantity
                    unit_quantity = original_total_quantity / original_servings

                adjusted_nutritions.append({
                    "name": name,
                    "total_quantity": round(new_total_quantity, 2),
                    "unit_serving": round(unit_quantity, 2),
                    "unit": unit
                })

            return adjusted_nutritions

        except Exception as e:
            logger.error(f"Database error occurred: {str(e)}")
            return {"error": "Database error occurred", "details": str(e)}, 400

    @staticmethod
    def get_recipe_by_origin(origin):
        """
        get the origin to avoid duplication in the database
        """
        origin_recipe = Recipe.query.filter_by(origin=origin).first()

        if origin_recipe:
            return origin_recipe
