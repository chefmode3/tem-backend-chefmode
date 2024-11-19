from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.user import User, UserRecipe, AnonymousUserRecipe

from app.models.anonymous_user import AnonymousUser
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.process import Process
from app.models.payment import Payment


class RecipeService:

    @staticmethod
    def save_recipe_data(data, user_id=None, anonymous_user_identifier=None):
        """
        Save a complete recipe with ingredients, processes, and user/anonymous association.
        :param data: JSON data for the recipe
        :param user_id: ID of the authenticated user (if any)
        :param anonymous_user_identifier: Identifier for the anonymous user (if any)
        :return: A dictionary with the saved recipe's details
        """
        try:
            recipe = RecipeService._save_recipe(data)

            if 'ingredients' in data:
                RecipeService._add_ingredients(recipe.id, data['ingredients'])

            if 'processes' in data:
                RecipeService._add_processes(recipe.id, data['processes'])

            if user_id:
                RecipeService._link_recipe_to_user(recipe.id, user_id)
            elif anonymous_user_identifier:
                RecipeService._link_recipe_to_anonymous_user(recipe.id, anonymous_user_identifier)
            else:
                raise ValueError("Either 'user_id' or 'anonymous_user_identifier' must be provided.")

            db.session.commit()

            return RecipeService._format_recipe_response(recipe)

        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Unexpected error: {str(e)}")

    @staticmethod
    def _save_recipe(data):
        """
        Save a recipe without ingredients or processes.
        """
        if not data.get('title') or not data.get('description'):
            raise ValueError("Recipe title and description are required.")

        recipe = Recipe(
            title=data.get('title'),
            servings=data.get('servings'),
            preparation_time=data.get('preparation_time'),
            description=data.get('description'),
            image_url=data.get('image_url'),
        )
        db.session.add(recipe)
        db.session.flush()

        return recipe

    @staticmethod
    def _add_ingredients(recipe_id, ingredients_data):
        """
        Add ingredients to a recipe along with their nutrients.
        """
        for ingredient_data in ingredients_data:
            ingredient = Ingredient(
                name=ingredient_data.get('name'),
                quantity=ingredient_data.get('quantity'),
                unit=ingredient_data.get('unit'),
                recipe_id=recipe_id
            )
            db.session.add(ingredient)
            db.session.flush()

            if 'nutrition' in ingredient_data:
                RecipeService._add_nutrients(ingredient.id, ingredient_data['nutrition'])

    @staticmethod
    def _add_nutrients(ingredient_id, nutrients_data):
        """
        Add nutrients for a specific ingredient.
        """
        for nutrient_name, nutrient_details in nutrients_data.items():
            nutrient = Nutrient(
                name=nutrient_name,
                quantity=nutrient_details.get('quantity'),
                unit=nutrient_details.get('unit'),
                ingredient_id=ingredient_id
            )
            db.session.add(nutrient)

    @staticmethod
    def _add_processes(recipe_id, processes_data):
        """
        Add processes to a recipe.
        """
        for process_data in processes_data:
            process = Process(
                step_number=process_data.get('step_number'),
                instructions=process_data.get('instructions'),
                recipe_id=recipe_id
            )
            db.session.add(process)

    @staticmethod
    def _link_recipe_to_user(recipe_id, user_id, flag=False):
        """
        Link a recipe to an authenticated user.
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} does not exist.")

        user_recipe = UserRecipe(user_id=user.id, recipe_id=recipe_id, flag=flag)
        db.session.add(user_recipe)

    @staticmethod
    def _link_recipe_to_anonymous_user(recipe_id, anonymous_user_identifier):
        """
        Link a recipe to an anonymous user.
        """
        anonymous_user = AnonymousUser.query.filter_by(identifier=anonymous_user_identifier).first()
        if not anonymous_user:
            raise ValueError(f"Anonymous user with identifier {anonymous_user_identifier} does not exist.")

        anon_user_recipe = AnonymousUserRecipe(
            anonymous_user_id=anonymous_user.id, recipe_id=recipe_id, request_count=1
        )
        db.session.add(anon_user_recipe)

    @staticmethod
    def _format_recipe_response(recipe):
        """
        Format the recipe response to include its ingredients, processes, and nutrients.
        """
        return {
            "id": recipe.id,
            "title": recipe.title,
            "servings": recipe.servings,
            "preparation_time": recipe.preparation_time,
            "description": recipe.description,
            "image_url": recipe.image_url,
            "ingredients": [
                {
                    "name": ingredient.name,
                    "quantity": ingredient.quantity,
                    "unit": ingredient.unit,
                    "nutrition": [
                        {
                            "name": nutrient.name,
                            "quantity": nutrient.quantity,
                            "unit": nutrient.unit
                        }
                        for nutrient in ingredient.nutrients
                    ]
                }
                for ingredient in recipe.ingredients
            ],
            "processes": [
                {
                    "step_number": process.step_number,
                    "instructions": process.instructions
                }
                for process in recipe.processes
            ]
        }

    @staticmethod
    def get_recipe_by_id(recipe_id):
        """
        Get a recipe with its ingredients and processes by ID.
        """
        recipe = Recipe.query.options(
            joinedload(Recipe.ingredients),
            joinedload(Recipe.processes)
        ).filter_by(id=recipe_id).first()

        if not recipe:
            return None

        return recipe

    @staticmethod
    def get_all_recipes(page, page_size):
        """
        Get all recipes with pagination and related ingredients and processes.
        """
        query = Recipe.query.options(
            joinedload(Recipe.ingredients),
            joinedload(Recipe.processes)
        ).order_by(Recipe.id.desc())

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        return {
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
            "page_size": pagination.per_page,
            "data": pagination.items
        }

    @staticmethod
    def get_my_recipes(user_id, page, page_size):
        """
        Get recipes created by a specific user with pagination.
        """
        query = Recipe.query.join(UserRecipe).filter(
            UserRecipe.user_id == user_id
        ).options(
            joinedload(Recipe.ingredients),
            joinedload(Recipe.processes)
        ).order_by(Recipe.id.desc())

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        return {
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
            "page_size": pagination.per_page,
            "data": pagination.items
        }

    @staticmethod
    def flag_recipe(recipe_id, user_id):
        """
        Mark a recipe as flagged for a specific user.
        """
        user_recipe = UserRecipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()

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
                "data": pagination.items,
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": pagination.page,
                "page_size": pagination.per_page,
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