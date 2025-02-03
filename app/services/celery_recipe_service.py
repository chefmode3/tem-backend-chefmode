from __future__ import annotations

import json
import logging
import re

from flask import g

from app.extensions import db
from app.models import AnonymousUser
from app.models import AnonymousUserRecipe
from app.models import Ingredient
from app.models import Process
from app.models import Recipe
from app.models import UserRecipe
from app.models.nutrition import Nutrition
from flask import request

from app.services import RecipeService
from app.utils.utils import get_current_user

logger = logging.getLogger(__name__)


class RecipeCelService:

    # store each in nutrition
    @staticmethod
    def create_nutrition(nutrition_data: dict) -> Nutrition:
        nutrition = Nutrition(
            calories=nutrition_data.get('calories'),
            carbohydrates=nutrition_data.get('carbohydrates'),
            fats=nutrition_data.get('fats'),
            fiber=nutrition_data.get('fiber'),
            proteins=nutrition_data.get('proteins'),
            sodium=nutrition_data.get('sodium'),
            sugar=nutrition_data.get('sugar')
        )
        db.session.add(nutrition)
        db.session.commit()
        return nutrition

    @staticmethod
    def get_or_create_user_recipe(user_id: int, recipe_id: int) -> tuple[UserRecipe, bool]:
        """
        Vérifie si l'association user-recipe existe, sinon la crée.
        Retourne un tuple (user_recipe, created) où created est True si nouvelle association.
        """
        existing_user_recipe = UserRecipe.query.filter_by(
            user_id=user_id,
            recipe_id=recipe_id
        ).first()

        if existing_user_recipe:
            return existing_user_recipe, False

        return RecipeCelService.create_user_recipe(user_id, recipe_id), True

    @staticmethod
    def get_or_create_recipe(recipe_data: dict) -> tuple[Recipe, bool]:
        """
        Vérifie si une recette existe déjà, sinon la crée.
        Retourne un tuple (recipe, created) où created est True si une nouvelle recette a été créée.
        """
        servings_count, servings_unit = RecipeCelService.split_serving(recipe_data.get('servings'))
        # Recherche basée sur le titre et d'autres critères pertinents
        existing_recipe = RecipeService.get_recipe_by_origin(origin=recipe_data.get('origin'),)
        logger.error(f"user recipe: {existing_recipe}")
        if existing_recipe:
            return existing_recipe, False
        return RecipeCelService.create_recipe(recipe_data), True

    @staticmethod
    def split_serving(serving: str) -> tuple[int, str]:
        """
        Split the serving string into the count and unit.
        """
        if not serving:
            return 1, ''

        match = re.match(r'(\d+)\s*(.*)', serving)
        if match:
            servings_count = int(match.group(1))
            servings_unit = str(match.group(2).strip())
        else:
            servings_count = 1
            servings_unit = None
        return servings_count, servings_unit

    @staticmethod
    def create_recipe(recipe_data: dict, ingredients_data: dict = None, processes_data: dict = None) -> Recipe:

        servings_count, servings_unit = RecipeCelService.split_serving(recipe_data.get('servings'))
        recipe = Recipe(
            title=recipe_data.get('title'),
            image_url=recipe_data.get('image_url'),
            preparation_time=recipe_data.get('total_time'),
            servings=servings_count,
            unit_serving=servings_unit,
            origin=recipe_data.get('origin'),
            ingredients=recipe_data.get('ingredients'),
            processes=recipe_data.get('directions'),
            nutritions=recipe_data.get('nutrition'),
        )
        db.session.add(recipe)
        db.session.commit()
        return recipe

    @staticmethod
    def create_user_recipe(user_id: int, recipe_id: int):
        user_recipe = UserRecipe(
            user_id=user_id,
            recipe_id=recipe_id
        )
        db.session.add(user_recipe)
        db.session.commit()
        return user_recipe

    # store ingredient
    @staticmethod
    def create_ingredient(ingredient_data: dict, recipe: Recipe) -> Ingredient:
        # get the nutrition of the ingredient and the store it
        ingredient_nutrition = RecipeCelService.create_nutrition(ingredient_data.get('nutrition'))

        # create the ingredient and store it
        ingredient = Ingredient(
            name=ingredient_data.get('name'),
            quantity=ingredient_data.get('quantity'),
            unit=ingredient_data.get('unit'),
            nutrition_id=ingredient_nutrition.id,  # Lier la nutrition spécifique
            recipe_id=recipe.id  # Lier l'ingrédient à la recette
        )
        db.session.add(ingredient)
        db.session.commit()
        return ingredient

    # methode for adding process to recipe
    @staticmethod
    def create_process(process_data: dict, recipe: Recipe) -> Process:
        process = Process(
            step_number=process_data.get('step_number'),
            instructions=process_data.get('instructions'),
            recipe_id=recipe.id  # Lier le processus à la recette
        )
        db.session.add(process)
        db.session.commit()
        return process

    @staticmethod
    def get_recipe_by_origin(self):
        pass

    @staticmethod
    def clean_ingredients(ingredients):
        # Filter out ingredients where title is None or list is None/empty
        return [
            ingredient for ingredient in ingredients
            if RecipeCelService.is_valid_title(ingredient.get('title_of_ingredient').strip().lower())
               and RecipeCelService.is_valid_list(ingredient.get('list'))
               and len(RecipeCelService.is_valid_list(ingredient.get('list'))) > 0
        ]

    @staticmethod
    def clean_directions(directions):
        return [
            direction for direction in directions
            if RecipeCelService.is_valid_title(direction.get('title_of_direction', '').strip().lower())
               and RecipeCelService.is_valid_list(direction.get('list'))
               and len(RecipeCelService.is_valid_list(direction.get('list'))) > 0
        ]

    @staticmethod
    def is_valid_title(value):
        return value not in [None, 'None', 'Null', '']
    @staticmethod
    def is_valid_list(directions):
        return [direction for direction in directions if RecipeCelService.is_valid_title(direction) ]
    # main methode for json treatment and call other methode
    @staticmethod
    def convert_and_store_recipe(recipe_json: dict):
        # Extraire data from JSON
        recipe_data = recipe_json.get('content')
        user, is_authenticated = get_current_user()
        logger.error(f"recipe data: {not recipe_data.get('ingredients') or not recipe_data.get('directions') or not recipe_data.get('title')}")

        logger.error(f"user accel: {user}")


        if not recipe_data.get('ingredients') or not recipe_data.get('directions') or not recipe_data.get('title'):
            logger.warning(f"Recipe from {recipe_data.get('origin')} has no valid data. Not saved.")
            return {'error': 'Recipe has no valid data and was not saved.'}

        ingredients = recipe_data.get('ingredients', [])
        ingredients_clean = RecipeCelService.clean_ingredients(ingredients)

        if  not ingredients_clean:
            logger.warning(f"Recipe from {recipe_data.get('origin')} has no valid Recipe ingredients. Not saved.")
            return {'error': 'Recipe has no valid ingredients and was not saved.'}

        directions = recipe_data.get('directions', [])
        directions_clean = RecipeCelService.clean_directions(directions)

        if not directions_clean :
            logger.warning(f"Recipe from {recipe_data.get('origin')} has no valid Recipe directions. Not saved.")
            return {'error': 'Recipe has no valid directions and was not saved.'}

        # logger.info(json.dumps(recipe))
        recipe_data['directions'] = directions_clean
        recipe_data['ingredients'] = ingredients_clean
        #  create and store recipe
        recipe, _ = RecipeCelService.get_or_create_recipe(recipe_data)
        # link recipe to a user
        # logger.error(f"user accel lok: {user}")
        if is_authenticated:
            # logger.error(f"user accel s: {user}")
            RecipeCelService.get_or_create_user_recipe(user_id=user.id, recipe_id=recipe.id)
        else:
            # logger.error(f"user accel a: {user}")
            if user:
                anonymous_user, is_exist = RecipeCelService.get_or_create_anonyme_user(user.id)
            else:
                anonymous_user, is_exist = RecipeCelService.get_or_create_anonyme_user(None)
            RecipeCelService.create_anonyme_user_recipe(user=anonymous_user, recipe=recipe)
        # logger.error(f"user accel: {user}")
        return recipe

    @staticmethod
    def get_or_create_anonyme_user(user_id: str) -> tuple[AnonymousUser, bool]:
        if not user_id:
            user_id = request.headers.get('X-Client-UUID')
        existing_user = AnonymousUser.query.filter_by(
            id=user_id,
        ).first()

        if existing_user:
            return existing_user, False
        return RecipeCelService.create_user_anonyme(user_id), True

    @classmethod
    def create_anonyme_user_recipe(cls, user, recipe):
        user_recipe = AnonymousUserRecipe.query.filter_by(
            anonymous_user_id=user.id,
            recipe_id=recipe.id
        ).first()
        if not user_recipe:
            user_recipe = AnonymousUserRecipe(
                anonymous_user_id=user.id,
                recipe_id=recipe.id
            )
            db.session.add(user_recipe)
            db.session.commit()
        return user_recipe

    @classmethod
    def create_user_anonyme(cls, user_id):
        a_user = AnonymousUser.query.filter_by(
            id=user_id,
         ).first()

        if not a_user:
            user_anonyme = AnonymousUser(
                identifier=user_id
            )
            db.session.add(user_anonyme)
            db.session.commit()
            return user_anonyme
        return a_user

    @staticmethod
    def get_or_create_anonyme_user_recipe(recipe_data: dict) -> tuple[Recipe, bool]:
        """
        check if the recipe already or create it.
        Return a tuple (recipe, created).
        """
        # Recherche basée sur le titre et d'autres critères pertinents
        existing_recipe = Recipe.query.filter_by(
            title=recipe_data.get('title'),
            origin=recipe_data.get('origin'),
            preparation_time=recipe_data.get('preparation_time'),
            servings=recipe_data.get('servings')
        ).first()

        if existing_recipe:
            return existing_recipe, False
        return RecipeCelService.create_recipe(recipe_data), True
