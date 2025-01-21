from __future__ import annotations

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from celery.signals import task_failure
from celery.utils.log import get_task_logger

from app.serializers.recipe_serializer import RecipeSerializer
from app.services import RecipeCelService, AnonymeUserService
from app.services.usecase_logic import RecipeService
from app.utils.utils import get_current_user
from extractors import fetch_description

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=5, default_retry_delay=5)
def call_fetch_description(self, data):
    """
    Celery task to fetch description asynchronously

    Args:
        data: Input data for fetching description

    Returns:
        dict: Result containing status and fetched description
    """
    try:
        # Fetch the description
        existing_data = data.get('video_url')
        user_id = data.get('user')
        is_authenticated = data.get('is_authenticated')
        description_result = RecipeService.get_recipe_by_origin(origin=existing_data)
        if description_result:

            if is_authenticated:
                RecipeCelService.get_or_create_user_recipe(user_id, description_result.id)
            else:
                anonymous_user, is_exist = RecipeCelService.get_or_create_anonyme_user(user_id)
                RecipeCelService.create_anonyme_user_recipe(user=anonymous_user, recipe=description_result)

            return {
                'status': 'success',
                'find': True,
                'result': {
                        'content': RecipeSerializer().dump(description_result)
                    }
                }
        description_result = fetch_description(data)

        return {
            'status': 'success',
            'find': False,
            'result': description_result
        }

    except Exception as exc:
        logger.error(f"Error in fetch_description task: {str(exc)}")

        try:
            # Retry the task
            self.retry(exc=exc)
        except MaxRetriesExceededError as mascExs:
            return {'error': f"Error in fetch_description task: {str(exc)} after retrying {str(mascExs)}"}


@task_failure.connect
def handle_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    """
    Gestionnaire appelé lorsqu'une tâche échoue.
    """
    logger.error(f"Task {task_id} failed: {exception}")
    user, is_authenticated = get_current_user()
    if not is_authenticated:
        AnonymeUserService.decrement_request_count(user.id)
