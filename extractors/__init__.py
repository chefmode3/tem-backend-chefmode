from __future__ import annotations

import json
import logging
import os
import time
import uuid


from app.utils.s3_storage import upload_to_s3
from extractors.facebook import download_facebook_video
from extractors.instagram import download_instagram_video
from extractors.new_tiktok import download_video_new_tiktok
from extractors.new_youtube import download_youtube
from extractors.recipe_extractor_website import analyse_nutrition_base_ingredient
from extractors.recipe_extractor_website import scrape_and_analyze_recipe
from extractors.tiktok import download_tiktok
from extractors.video_analyzer import process_video
from extractors.x_scraper import download_twitter_video
from extractors.youtube import download_youtube_video
from utils.common import identify_platform
from utils.settings import BASE_DIR


logger = logging.getLogger(__name__)
# Constants
DOWNLOAD_FOLDER = BASE_DIR / 'downloads'
SLEEP_TIME = 2


def ensure_download_folder_exists():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)


def retry_process_video(output_filepath):
    # Retry logic for processing the video
    description = None
    retries = 0
    max_retries = 2  # set max retry attempts

    while description is None and retries < max_retries:
        description = process_video(output_filepath)

        if description is None:
            retries += 1
            time.sleep(2)  # Optional: wait before retrying

    return description


def fetch_description(request_data):
    try:
        video_url = request_data['video_url']
        platform = identify_platform(video_url)

        final_content, recipe, image_url = None, None, None

        # Ensure the download folder exists
        ensure_download_folder_exists()

        # Define the output file path
        os.path.join(DOWNLOAD_FOLDER, f'downloaded_video_{uuid.uuid4()}.mp4')

        # logger.info(output_filepath)
        # Dictionary to map platforms to their respective download functions
        download_functions = {
            'tiktok': download_video_new_tiktok,
            'youtube': download_youtube_video,
            'instagram': download_instagram_video,
            'x': download_twitter_video,
            'facebook': download_facebook_video
        }

        if platform in download_functions:
            # Download the video
            video_url_with_audio = download_functions[platform](video_url)
            logger.error(video_url_with_audio)
            # Wait for the download to complete
            time.sleep(SLEEP_TIME)
            if not video_url_with_audio:
                return {'error': 'video recipe not found ', 'status': 404}
            # Process the video
            recipe, image_url_to_store = retry_process_video(video_url_with_audio)
            s3_file_name = f'{uuid.uuid4()}_image.jpg'
            image_url = upload_to_s3(image_url_to_store, s3_file_name)

            # Remove the downloaded video after processing
            remove_file(video_url_with_audio)
            remove_file(image_url_to_store)

        elif platform == 'website':
            recipe, got_image, image_url = scrape_and_analyze_recipe(video_url)
        if not recipe:
            return {'error': 'recipe not found', 'status': 404}

        recipe_info = json.loads(recipe)

        nutrition = analyse_nutrition_base_ingredient(recipe)
        nutrition_json = json.loads(nutrition)
        logger.info(nutrition_json['nutritions'])
        recipe_info['nutrition'] = nutrition_json['nutritions']
        logger.info(image_url)
        recipe_info['image_url'] = image_url
        recipe_info['origin'] = video_url
        logger.info(json.loads(recipe))
        logger.error(f"recipe_info { recipe_info}")
        final_content = {
            'content': recipe_info,
        }

        return final_content
    except json.JSONDecodeError as e:
        logger.error(f"An error occurred while decoding JSON: {e}")
        return None #'(request_data)
    except Exception as e:

        logger.error(f"An error occurred while fetching the description.{e}")
    return None


def remove_file(file_path_to_remove):
    if os.path.exists(file_path_to_remove):
        os.remove(file_path_to_remove)
