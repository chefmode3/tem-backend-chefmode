from __future__ import annotations

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from celery.utils.log import get_task_logger

from app.serializers.recipe_serializer import RecipeSerializer
from app.services.usecase_logic import RecipeService
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
        description_result = RecipeService.get_recipe_by_origin(origin=existing_data)
        if description_result:

            return {
                'status': 'success',
                'find': True,
                'result': RecipeSerializer().dump(description_result)
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
