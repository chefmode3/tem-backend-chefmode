import http.client
import json
import logging
import re

import requests

from utils.common import save_video_to_file

logger = logging.getLogger(__name__)


def download_instagram_video(instagram_url, output_filename="downloaded_video.mp4"):
    # Step 1: Extract the shortcode from the provided Instagram URL
    match = re.search(r"(?:reels?|p)/([^/?#&]+)", instagram_url)

    if not match:
        raise ValueError("Invalid Instagram URL. Could not extract shortcode.")

    shortcode = match.group(1)  # Extract the actual shortcode
    logger.info(f"Extracted shortcode: {shortcode}")

    # Step 2: Make the API request
    conn = http.client.HTTPSConnection("instagram-api-20231.p.rapidapi.com")
    headers = {
        "x-rapidapi-key": "1776083f1dmsh864701c7fc5a69dp1d97f3jsn8cb7620cf8c2",
        "x-rapidapi-host": "instagram-api-20231.p.rapidapi.com"
    }

    conn.request("GET", f"/api/media_info_from_shortcode/{shortcode}", headers=headers)
    res = conn.getresponse()
    data = res.read()

    # Step 3: Parse the JSON response
    response = json.loads(data.decode("utf-8"))

    # Step 4: Extract video URL
    try:
        video_versions = response['data']['items'][0]['video_versions']
        video_url = video_versions[0]['url']  # Use the first available video URL
        logger.info(f"Downloading video from: {video_url}")
    except (KeyError, IndexError):
        logger.info("Error: Could not extract video URL.")
        return

    # Step 5: Download the MP4 video
    try:
        video_response = requests.get(video_url, stream=True)
        if video_response.status_code != 200:
            logger.info("Failed to download the video.")
            return None
        video_buffer = video_response.content
        return save_video_to_file(video_buffer)
    except Exception as e:
        logger.info(f"Error downloading video: {e}")
