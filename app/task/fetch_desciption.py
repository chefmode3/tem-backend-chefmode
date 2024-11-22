from app.extensions import celery
from celery.utils.log import get_task_logger
from app.services import RecipeCelService
from celery.exceptions import MaxRetriesExceededError

from extractors import fetch_description
from app.services.usecase_logic import RecipeService

logger = get_task_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=5)
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
        if not description_result:
            description_result = fetch_description(data)

        return {
            'status': 'success',
            'result': description_result
        }

    except Exception as exc:
        logger.error(f"Error in fetch_description task: {str(exc)}")

        try:
            # Retry the task
            self.retry(exc=exc)

        except MaxRetriesExceededError:
            return {'error': f"Error in fetch_description task: {str(exc)}" }
