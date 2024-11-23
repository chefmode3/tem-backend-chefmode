import json
import logging

from celery.result import AsyncResult
from marshmallow import ValidationError

from app.serializers.recipe_serializer import LinkRecipeSchema, TaskIdSchema
from flask_restx import Namespace, Resource
from flask import request, abort, jsonify
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.task.fetch_desciption import call_fetch_description

logger = logging.getLogger(__name__)

recipe_ns = Namespace('recipe', description="user recipe")
link_recipe_schema = LinkRecipeSchema()
link_recipe_model = convert_marshmallow_to_restx_model(recipe_ns, link_recipe_schema)
task_id_schema = TaskIdSchema()
task_id_model = convert_marshmallow_to_restx_model(recipe_ns, task_id_schema)


@recipe_ns.route('/gen_recipe')
class RecipeScrap(Resource):
    @recipe_ns.expect(link_recipe_model)
    @recipe_ns.response(200, "Recipe fetched successfully", model=link_recipe_model)
    @recipe_ns.response(404, "Recipe not found")
    def post(self):
        try:
            link = LinkRecipeSchema().load(request.get_json())
            data = {
                "video_url": link.get('link'),
            }
            task = call_fetch_description.delay(data)
            return {'task_id': task.id}, 200
        except ValidationError as form_ee:
            abort(400, description=form_ee.messages)
        except Exception as e:
            abort(400, description=str(e))


@recipe_ns.route('/fetch_results/<string:task_id>/')
class RecipeScrapPost(Resource):
    @recipe_ns.response(200, "Recipe fetched successfully", model=link_recipe_model)
    @recipe_ns.response(404, "Recipe not found")
    def get(self, task_id):
        try:

            TaskIdSchema().load({"task_id": task_id})
        except ValidationError as ve:
            abort(400, description=ve.messages)

        try:
            res = AsyncResult(task_id)
        except Exception as e:
            abort(400, description=f"Invalid task ID: {str(e)}")

        if res.state == 'PENDING':
            return {"status": "PENDING"}, 202
        elif res.state == 'SUCCESS':
            result: dict = res.result

            content = result.get('result')
            find = result.get('find')
            if find:
                return content

            logger.info(json.dumps(content, indent=4))
            # data = json.loads(result.get('content'))
            # recipe = RecipeCelService.convert_and_store_recipe(content)

            return content #RecipeSerializer().dump(recipe), 200
        elif res.state == 'FAILURE':
            return {"status": "FAILURE", "message": str(res.result)}, 500
        else:
            return {"status": res.state}, 202
