from __future__ import annotations

import logging
import os

from celery.result import AsyncResult
from flask import abort, g
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
from app.utils.utils import get_current_user


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
            user, is_authenticated = get_current_user()

            data = {
                'video_url': link.get('link'),
                'user': user.id,
                'is_authenticated': is_authenticated

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
        logger.error("find")
        try:
            res = AsyncResult(task_id)
        except Exception as e:
            abort(400, description=f"Invalid task ID: {str(e)}")
        # logger.error("eee")
        try:
            if res.state == 'PENDING':
                return {'status': 'PENDING'}, 202
            elif res.state == 'SUCCESS':
                result: dict = res.result

                content = result.get('result')
                # logger.error("eee12")
                # logger.info(content)
                find = result.get('find')
                logger.error(find)
                if not content:
                    return {'error': "recipe not found please Retry later "}, 404
                if content.get('error'):
                    return content, content.pop('status')
                # logger.error("find wes")
                if not find:
                    # logger.error('test of saving in a database')
                    content = RecipeCelService.convert_and_store_recipe(content)
                    content = RecipeSerializer().dump(content)
                    app_settings = os.getenv('APP_SETTINGS')
                    if app_settings == 'app.config.ProductionConfig':
                        frontend_recipe_base_url = os.getenv('FRONTEND_RECIPE_BASE_URL')
                        recipe_chefmode_url = f"{frontend_recipe_base_url}/{content.get('id')}"
                        send_slack_notification_recipe(content.get('origin'), 'New recipe generated', recipe_chefmode_url)
                return content, 200

            elif res.state == 'FAILURE':
                return {'status': 'FAILURE', 'message': str(res.result)}, 400
            else:
                return {'status': res.state}, 202
        except Exception as e:
            logger.error(f"unpexted request occured {e}, 500")
            abort(400, description=f"unpexted request occured")
