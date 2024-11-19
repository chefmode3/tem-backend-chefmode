from app.extensions import db
from app.models import Nutrition, Recipe, Ingredient, Process, UserRecipe, AnonymousUserRecipe
from app.services import UserService


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
    def get_or_create_recipe(recipe_data: dict) -> tuple[Recipe, bool]:
        """
        Vérifie si une recette existe déjà, sinon la crée.
        Retourne un tuple (recipe, created) où created est True si une nouvelle recette a été créée.
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

    @staticmethod
    def create_recipe(recipe_data: dict) -> Recipe:

            recipe = Recipe(
                title=recipe_data.get('title'),
                description=recipe_data.get('description'),
                image_url=recipe_data.get('image_url'),
                preparation_time=recipe_data.get('preparation_time'),
                servings=recipe_data.get('servings'),
                origin=recipe_data.get('origin')
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe


    @staticmethod
    def create_user_recipe(user_id:int, recipe_id:int):
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

    # main methode for json traitement and call other methode
    @staticmethod
    def convert_and_store_recipe(recipe_json: dict):
        # Extraire data from JSON
        recipe_data = recipe_json.get('content')
        print(recipe_data.get('origin'))
        user = UserService.get_current_user()

        recipe_info = recipe_data.get('recipe_information')
        recipe_info['origin'] = recipe_json['origin']

        ingredients_data = recipe_data.get('ingredients')
        processes_data = recipe_data.get('processes')

        # create and store recipe
        recipe, _ = RecipeCelService.get_or_create_recipe(recipe_info)
        if user:
            RecipeCelService.create_user_recipe(user_id=user['id'], recipe_id=recipe.id)
        else:
            RecipeCelService.create_anonyme_user_recipe(user_id=user.id, recipe_id=recipe.id)

        # # add the  ingrédients
        for ingredient in ingredients_data:
            RecipeCelService.create_ingredient(ingredient, recipe)
        #
        # # add step to recipe
        for process in processes_data:
            RecipeCelService.create_process(process, recipe)

    @classmethod
    def create_anonyme_user_recipe(cls, user_id, recipe_id):
        user_recipe = AnonymousUserRecipe(
            anonymous_user_id=user_id,
            recipe_id=recipe_id
        )
        db.session.add(user_recipe)
        db.session.commit()
        return user_recipe
        pass

