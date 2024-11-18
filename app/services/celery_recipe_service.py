from app.extensions import db
from app.models import Nutrition, Recipe, Ingredient, Process



class RecipeCelService:


    # store each in nutrition
    @staticmethod
    def create_nutrition(nutrition_data: dict) -> Nutrition:
        nutrition = Nutrition(
            calories=nutrition_data['calories'],
            carbohydrates=nutrition_data['carbohydrates'],
            fats=nutrition_data['fats'],
            fiber=nutrition_data['fiber'],
            proteins=nutrition_data['proteins'],
            sodium=nutrition_data['sodium'],
            sugar=nutrition_data['sugar']
        )
        db.session.add(nutrition)
        db.session.commit()
        return nutrition

    @staticmethod
    def create_recipe(self, recipe_data: dict) -> Recipe:
        recipe = Recipe(
            title=recipe_data['title'],
            description=recipe_data['description'],
            image_url=recipe_data['image_url'],
            preparation_time=recipe_data['preparation_time'],
            servings=recipe_data['servings']
        )
        db.session.add(recipe)
        db.session.commit()
        return recipe

    # store ingredient
    @staticmethod
    def create_ingredient(ingredient_data: dict, recipe: Recipe) -> Ingredient:
        # get the nutrition of the ingredient and the store it
        ingredient_nutrition = RecipeCelService.create_nutrition(ingredient_data['nutrition'])

        # create the ingredient and store it
        ingredient = Ingredient(
            name=ingredient_data['name'],
            quantity=ingredient_data['quantity'],
            unit=ingredient_data['unit'],
            nutrition=ingredient_nutrition,  # Lier la nutrition spécifique
            recipe=recipe  # Lier l'ingrédient à la recette
        )
        db.session.add(ingredient)
        db.session.commit()
        return ingredient

    # methode for adding process to recipe
    @staticmethod
    def create_process(process_data: dict, recipe: Recipe) -> Process:
        process = Process(
            step_number=process_data['step_number'],
            instructions=process_data['instructions'],
            recipe=recipe  # Lier le processus à la recette
        )
        db.session.add(process)
        db.session.commit()
        return process

    # main methode for json traitement and call other methode
    @staticmethod
    def convert_and_store_recipe(recipe_json: dict):
        # Extraire data from JSON
        recipe_data = recipe_json['content']
        recipe_info = recipe_data['recipe_information']
        ingredients_data = recipe_data['ingredients']
        processes_data = recipe_data['processes']

        # create and store recipe
        recipe = RecipeCelService.create_recipe(recipe_info)

        # add the  ingrédients
        for ingredient in ingredients_data:
            RecipeCelService.create_ingredient(ingredient, recipe)

        # add step to recipe
        for process in processes_data:
            RecipeCelService.create_process(process, recipe)

