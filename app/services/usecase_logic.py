from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.anonymous_user import AnonymousUser
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.process import Process
from app.models.nutrition import Nutrition

class RecipeService:

    @staticmethod
    def get_recipe_by_id(recipe_id):
        """
        Get a recipe with its ingredients and processes by ID.
        """
        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            return None

        return recipe

    @staticmethod
    def get_all_recipes(page, page_size):
        """
        Get all recipes with pagination and related ingredients and processes.
        """
        query = Recipe.query.order_by(Recipe.id.desc())
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
                    "flag": recipe.flag,
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
    def get_my_recipes(user_id, page, page_size):
        """
        Get recipes created by a specific user with pagination.
        """
        query = Recipe.query.join(UserRecipe).filter(
            UserRecipe.user_id == user_id
        ).order_by(Recipe.id.desc())

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
                    "flag": recipe.flag,
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
        user_recipe = Recipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()

        if not user_recipe:
            return None
        user_recipe.flag = True
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, description=f"Database error: {str(e)}")

        return {"message": "Recipe flagged successfully."}

    @staticmethod
    def is_recipe_flagged_by_user(recipe_id, user_id):
        """
        Check if a recipe is flagged by the current user.
        """
        user_recipe = Recipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()

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
                        "flag": recipe.flag,
                        "preparation_time": recipe.preparation_time,
                        "description": recipe.description,
                        "image_url": recipe.image_url,
                        "ingredients": recipe.ingredients,
                        "processes": recipe.processes,
                    }
                    for recipe in pagination.items
                ]
            }
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error: {str(e)}")

    @staticmethod
    def get_nutrition_by_ingredient(ingredient_id):
        """
        Fetch nutrition data for a specific ingredient.
        :param ingredient_id: ID of the ingredient
        :return: List of nutrients associated with the ingredient
        """
        try:
            nutrients = Nutrition.query.filter_by(ingredient_id=ingredient_id).all()
            if not nutrients:
                return None

            return nutrients
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")