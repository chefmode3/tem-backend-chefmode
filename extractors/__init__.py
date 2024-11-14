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


def retry_process_video(output_filename):
    # Retry logic for processing the video
    description = None
    retries = 0
    max_retries = 2  # set max retry attempts

    while description is None and retries < max_retries:
        description = process_video(output_filename)

        if description is None:
            retries += 1
            time.sleep(2)  # Optional: wait before retrying

    return description
    # if description:
    #     try:
    #         st.image("recipe_image.jpg")
    #     except Exception as e:
    #         st.warning(f"Could not display image. Error: {e}")
    #     st.markdown(description, unsafe_allow_html=True)
    # else:
    #     st.error("Failed to retrieve the description after multiple attempts.")


def fetch_description(request_data):
    video_url = request_data["video_url"]
    platform = identify_platform(video_url)

    final_content, recipe, image_url = None, None, None
    if platform == "tiktok":
        download_tiktok(video_url)

        output_filename = "downloaded_video.mp4"
        time.sleep(2)
        recipe = retry_process_video(output_filename)

    elif platform == "youtube":
        download_youtube(video_url, output_filename="downloaded_video.mp4")

        time.sleep(2)
        output_filename = "downloaded_video.mp4"
        recipe = retry_process_video(output_filename)

    elif platform == "instagram":
        download_instagram_video(video_url)

        time.sleep(2)
        output_filename = "downloaded_video.mp4"
        recipe = retry_process_video(output_filename)

    elif platform == "x":
        download_twitter_video(video_url)
        time.sleep(2)
        output_filename = "downloaded_video.mp4"

        recipe = retry_process_video(output_filename)

    elif platform == "facebook":
        download_facebook_video(video_url)
        time.sleep(2)
        output_filename = "downloaded_video.mp4"

        recipe = retry_process_video(output_filename)

    elif platform == "website":
        recipe, got_image, image_url = scrape_and_analyze_recipe(video_url)

    final_content = {
        "content": json.loads(recipe),
    }
    if image_url is not None:
        final_content.update({"image_url": image_url})
    return final_content

