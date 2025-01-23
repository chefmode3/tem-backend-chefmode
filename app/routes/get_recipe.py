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
from app.services.user_service import UserService
from app.services import RecipeCelService
from app.services.usecase_logic import RecipeService
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
        # logger.error(f"find wes {res.state}")
        try:
            res = AsyncResult(task_id)
        except Exception as e:
            abort(400, description=f"Invalid task ID: {str(e)}")
        # logger.error("eee")
        try:
            if res.state == 'PENDING':
                return {'status': 'PENDING'}, 202
            elif res.state == 'SUCCESS':
                res_result_dict: dict = res.result

                fetch_result = res_result_dict.get('result')

                if not fetch_result:
                    return {'error': "recipe not found please Retry later "}, 404
                if fetch_result.get('error'):
                    return fetch_result, fetch_result.pop('status')
                # logger.error("find wes")
                fetch_result_content = fetch_result.get('content')
                recipe = RecipeService.get_recipe_by_origin(fetch_result_content.get('origin'))
                if not recipe:
                    # logger.error('test of saving in a database')
                    fetch_result_content = RecipeCelService.convert_and_store_recipe(fetch_result)
                    fetch_result_content = RecipeSerializer().dump(fetch_result_content)
                    app_settings = os.getenv('APP_SETTINGS')
                    if app_settings == 'app.config.ProductionConfig':
                        frontend_recipe_base_url = os.getenv('FRONTEND_RECIPE_BASE_URL')
                        recipe_chefmode_url = f"{frontend_recipe_base_url}/{fetch_result_content.get('id')}"
                        user = UserService.get_user_by_token()
                        user_id = user.id if user else None
                        send_slack_notification_recipe(fetch_result_content.get('origin'), 'New recipe generated', recipe_chefmode_url, user_id=user_id)
                            
                return RecipeSerializer().dump(recipe), 200

            elif res.state == 'FAILURE':
                return {'status': 'FAILURE', 'message': str(res.result)}, 400
            else:
                return {'status': res.state}, 202
        except Exception as e:
            logger.error(f"unexpected request occured {e}, 500")
            abort(400, description=f"unpexted request occured")
