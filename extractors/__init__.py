import os
import re

from extractors.facebook import download_facebook_video
from extractors.tiktok import download_tiktok
from extractors.new_youtube import download_youtube
from extractors.instagram import download_instagram_video
from extractors.video_analyzer import process_video
import time
from extractors.recipe_extractor_website import scrape_and_analyze_recipe
from extractors.x_scraper import download_twitter_video
from utils.common import identify_platform
import json

from utils.settings import BASE_DIR

# Constants
DOWNLOAD_FOLDER = BASE_DIR / "downloads"
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
    video_url = request_data["video_url"]
    platform = identify_platform(video_url)

    final_content, recipe, image_url = None, None, None

    # Ensure the download folder exists
    ensure_download_folder_exists()

    # Define the output file path
    output_filepath = os.path.join(DOWNLOAD_FOLDER, "downloaded_video.mp4")

    print(output_filepath)
    # Dictionary to map platforms to their respective download functions
    download_functions = {
        "tiktok": download_tiktok,
        "youtube": download_youtube,
        "instagram": download_instagram_video,
        "x": download_twitter_video,
        "facebook": download_facebook_video
    }

    if platform in download_functions:
        # Download the video
        download_functions[platform](video_url)

        # Wait for the download to complete
        time.sleep(SLEEP_TIME)

        # Process the video
        recipe = retry_process_video(output_filepath)

        # Remove the downloaded video after processing
        if os.path.exists(output_filepath):
            os.remove(output_filepath)

    elif platform == "website":
        recipe, got_image, image_url = scrape_and_analyze_recipe(video_url)

    print(json.loads(recipe))
    final_content = {
        "content": json.loads(recipe),
        "origin": video_url,
        "image_url": image_url
    }

    return final_content

