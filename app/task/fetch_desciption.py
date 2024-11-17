from app.extensions import celery
from celery.utils.log import get_task_logger
from app.services.celery_recipe_service import RecipeTaskService
from celery.exceptions import MaxRetriesExceededError

from extractors import fetch_description


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
        description_result = fetch_description(data)

        # Update task result in database
        RecipeTaskService.update_task_result(
            task_id=self.request.id,
            status='SUCCESS',
            result=description_result
        )

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
            # Update database with failure status
            RecipeTaskService.update_task_result(
                task_id=self.request.id,
                status='FAILURE',
                error=str(exc)
            )

            # Re-raise the exception
            raise exc
