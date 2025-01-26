from celery import current_task, shared_task

from app.utils.utils import with_app_context


from extractors.tiktok_d1 import get_tiktok_video


@shared_task
@with_app_context
def run_tiktok_downloader(video_url):

    return get_tiktok_video(video_url)  # Return the result of the function
