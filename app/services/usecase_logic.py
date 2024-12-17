from __future__ import annotations

import logging
import re
from fractions import Fraction

from app.extensions import db
from app.models.recipe import Recipe
from app.models.user import UserRecipe
# from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class RecipeService:

    @staticmethod
    def get_recipe_by_id(recipe_id: str, serving: str = None):
        """
        Get a recipe with its ingredients and processes by ID.
        """
        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            return None
        if not serving:
            return recipe

        serving = int(serving)
        unit_serving = recipe.unit_serving
        match = re.search(r'(\d+)\s*(.*)', unit_serving)
        if match:
            servings_count = int(match.group(1))
            start_position = match.start(1)
            end_position = match.end(1)
            logger.info(f"unit_serving {unit_serving} to {servings_count} at position {start_position} {end_position}")

            # Extract the new value based on the position
            old_value = unit_serving[start_position:end_position]
            new_value = str(servings_count - serving)
            servings_unit = str(match.group(2).strip())
            recipe.unit_serving = f"{servings_unit} {new_value}"
            logger.info(f"unit_serving: {servings_unit} {old_value} to {new_value}")
        old_serving = recipe.servings

        ingredients = recipe.ingredients

        # recipe.ingredients = adjust_ingredients(ingredients, serving, old_serving)
        logger.error('position123')
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
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'page_size': pagination.per_page,
            'data': [recipe for recipe in pagination.items]
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
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'page_size': pagination.per_page,
            'data': [recipe for recipe in pagination.items]
        }

    @staticmethod
    def flag_recipe(recipe_id, user_id):
        """
        Mark a recipe as flagged for a specific user.
        """
        user_recipe = UserRecipe.query.filter_by(
            user_id=user_id, recipe_id=recipe_id
        ).first()

        if not user_recipe:
            return None
        user_recipe.flag = not user_recipe.flag

        try:
            db.session.commit()
            return {
                'message': 'Recipe flag status updated successfully.',
                'flag': user_recipe.flag
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error occurred: {str(e)}")
            return {'error': 'Database error occurred', 'details': str(e)}, 400

    @staticmethod
    def is_recipe_flagged_by_user(recipe_id, user_id):
        """
        Check if a recipe is flagged by the current user.
        """
        user_recipe = UserRecipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()

        if not user_recipe:
            return None

        return {'flagged': user_recipe.flag}

    @staticmethod
    def search_recipes(search_term, current_user, page=1, page_size=10):
        """
        Search for recipes by title with pagination.
        """
        try:
            query = Recipe.query.join(UserRecipe).filter(
                UserRecipe.user_id == current_user['id'],
                Recipe.title.ilike(f"%{search_term}%")
            )

            pagination = query.paginate(page=page, per_page=page_size, error_out=False)

            return {
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'page_size': pagination.per_page,
                'data': [recipe for recipe in pagination.items]
            }
        except Exception as e:
            logger.error(f"Database error occurred: {str(e)}")
            return {'error': 'Database error occurred', 'details': str(e)}, 400

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
                name = nutrition.get('name')
                original_total_quantity = nutrition.get('quantity')
                unit = nutrition.get('unit')

                if serving:
                    new_total_quantity = (serving * original_total_quantity) / original_servings
                    unit_quantity = new_total_quantity / serving
                else:
                    new_total_quantity = original_total_quantity
                    unit_quantity = original_total_quantity / original_servings

                adjusted_nutritions.append({
                    'name': name,
                    'total_quantity': round(new_total_quantity, 2),
                    'unit_serving': round(unit_quantity, 2),
                    'unit': unit
                })

            return adjusted_nutritions

        except Exception as e:
            logger.error(f"Database error occurred: {str(e)}")
            return {'error': 'Database error occurred', 'details': str(e)}, 400

    @staticmethod
    def get_recipe_by_origin(origin):
        """
        get the origin to avoid duplication in the database
        """
        origin_recipe = Recipe.query.filter_by(origin=origin).first()
        logger.error(f'video url: {origin}')
        if origin_recipe:
            return origin_recipe
        return None


def adjust_ingredients(ingredients, serving_factor, original_serving):
    updated_ingredients = []

    # Calcul du facteur d'ajustement sous forme de Fraction
    scaling_factor = Fraction(serving_factor, original_serving)

    for line in ingredients:
        # Trouver toutes les quantités (entiers et fractions) dans la ligne
        matches = re.findall(r'\d+\s+\d+/\d+|\d+/\d+|\d+', line)
        if matches:
            updated_line = line
            for match in matches:
                # Convertir le match en Fraction
                if ' ' in match:  # Nombre mixte (ex : "2 1/2")
                    whole_part, fraction_part = match.split()
                    original_value = Fraction(int(whole_part)) + Fraction(fraction_part)
                elif '/' in match:  # Fraction simple (ex : "1/2")
                    original_value = Fraction(match)
                else:  # Entier (ex : "4")
                    original_value = Fraction(int(match))

                # Ajuster la valeur selon le facteur de mise à l'échelle
                adjusted_value = original_value * scaling_factor

                # Convertir en format mixte ou garder le format Fraction
                if adjusted_value.denominator == 1:  # Si c'est un entier
                    adjusted_value_str = str(adjusted_value.numerator)
                elif adjusted_value.numerator > adjusted_value.denominator:  # Nombre mixte
                    whole_part = adjusted_value.numerator // adjusted_value.denominator
                    fractional_part = Fraction(adjusted_value.numerator % adjusted_value.denominator, adjusted_value.denominator)
                    adjusted_value_str = f"{whole_part} {fractional_part}"
                else:  # Fraction propre
                    adjusted_value_str = str(adjusted_value)

                # Remplacer dans la ligne d'ingrédient
                updated_line = updated_line.replace(match, adjusted_value_str, 1)

            updated_ingredients.append(updated_line)
        else:
            # Si aucune quantité n'est trouvée, ajouter la ligne telle quelle
            updated_ingredients.append(line)

    return updated_ingredients
