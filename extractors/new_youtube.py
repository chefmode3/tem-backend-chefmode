import re
import os
import json
import logging
import http.client

import requests


from utils.common import save_video_to_file, download_youtube_video

logger = logging.getLogger(__name__)


def extract_video_id(youtube_url):
    # Regular expression to extract the video ID from various YouTube URL formats
    match = re.search(r"(?:v=|\/(vi|v|shorts)\/|\/embed\/|youtu\.be\/)([a-zA-Z0-9_-]{11})", youtube_url)
    if match:
        return match.group(2)
    else:
        logger.info("Error: Unable to extract video ID.")
        return None


def download_youtube(youtube_url, output_filename="downloaded_video.mp4"):
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return

    conn = http.client.HTTPSConnection("youtube-media-downloader.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "f2d1322fc9mshd04f3762ac0793ep11069cjsn4e55258922af",
        'x-rapidapi-host': "youtube-media-downloader.p.rapidapi.com"
    }

    # Request video details using the video ID
    conn.request("GET", f"/v2/video/details?videoId={video_id}", headers=headers)
    res = conn.getresponse()
    data = res.read()

    # Parse JSON response
    response = json.loads(data.decode("utf-8"))

    try:
        video_streams = response['videos']['items']
        video_url_with_audio = video_streams[0].get('url')
        if not video_url_with_audio:
            logger.info("Error: No valid video URL found.")
            return None
        logger.info("Downloading video into memory...")
        video_response = requests.get(video_url_with_audio, stream=True)
        if video_response.status_code != 200:
            logger.info("Failed to download the video.")
            return download_youtube_video(youtube_url)
        video_buffer = video_response.content
        # logger.info(video_buffer)
        return save_video_to_file(video_buffer)

    except (KeyError, IndexError):
        logger.error(f"Error: Unable to fetch video details., {(KeyError, IndexError)} ")
        # return None
    return download_youtube_video(youtube_url)
# Download the video
    # try:
    #     urllib.request.urlretrieve(video_url, output_filename)
    #     logger.info(f"Video downloaded successfully as {output_filename}")
    # except Exception as e:
    #     logger.info(f"Error downloading video: {e}")

# # Example usage:
# youtube_url = "https://www.youtube.com/watch?v=1LzFy7Rr89E"  # Or a Shorts URL
# download_youtube_video(youtube_url)


