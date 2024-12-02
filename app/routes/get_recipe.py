from __future__ import annotations

import logging

from celery.result import AsyncResult
from flask import abort
from flask import request
from flask_restx import Namespace
from flask_restx import Resource
from marshmallow import ValidationError

from app.decorateur.anonyme_user import load_or_create_anonymous_user
from app.decorateur.anonyme_user import track_anonymous_requests
from app.serializers.recipe_serializer import LinkRecipeSchema
from app.serializers.recipe_serializer import RecipeSerializer
from app.serializers.recipe_serializer import TaskIdSchema
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.services import RecipeCelService
from app.task.fetch_desciption import call_fetch_description
from app.utils.slack_hool import send_slack_notification_recipe

logger = logging.getLogger(__name__)

recipe_ns = Namespace('recipe', description='user recipe')

link_recipe_schema = LinkRecipeSchema()
link_recipe_model = convert_marshmallow_to_restx_model(recipe_ns, link_recipe_schema)
task_id_schema = TaskIdSchema()
task_id_model = convert_marshmallow_to_restx_model(recipe_ns, task_id_schema)


@recipe_ns.route('/gen_recipe')
class RecipeScrap(Resource):
    @recipe_ns.expect(link_recipe_model)
    @recipe_ns.response(200, 'Recipe fetched successfully', model=link_recipe_model)
    @recipe_ns.response(404, 'Recipe not found')
    @load_or_create_anonymous_user
    @track_anonymous_requests
    def post(self):
        try:
            link = LinkRecipeSchema().load(request.get_json())
            data = {
                'video_url': link.get('link'),
            }

            task = call_fetch_description.delay(data)
            return {'task_id': task.id}, 200
        except ValidationError as form_ee:
            abort(400, description=form_ee.messages)
        except Exception as e:
            abort(400, description=str(e))


@recipe_ns.route('/fetch_results/<string:task_id>/')
class RecipeScrapPost(Resource):
    @recipe_ns.response(200, 'Recipe fetched successfully', model=link_recipe_model)
    @recipe_ns.response(404, 'Recipe not found')
    def get(self, task_id):
        try:

            TaskIdSchema().load({'task_id': task_id})
        except ValidationError as ve:
            abort(400, description=ve.messages)

        try:
            res = AsyncResult(task_id)
        except Exception as e:
            abort(400, description=f"Invalid task ID: {str(e)}")

        if res.state == 'PENDING':
            return {'status': 'PENDING'}, 202
        elif res.state == 'SUCCESS':
            result: dict = res.result

            content = result.get('result')
            find = result.get('find')
            if content.get('error'):
                return content, content.pop('status')

            # logger.error(json.dumps(content, indent=4))
            # data = json.loads(result.get('content'))

            if not find:
                content = RecipeCelService.convert_and_store_recipe(content)
                content = RecipeSerializer().dump(content)
            send_slack_notification_recipe(content.get('origin'))
            return content, 200

        elif res.state == 'FAILURE':
            return {'status': 'FAILURE', 'message': str(res.result)}, 400
        else:
            return {'status': res.state}, 202
