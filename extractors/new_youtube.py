import os
import re
import logging

import requests


from utils.common import download_youtube_video, pytube_download_video

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
    
    host = os.getenv("RESIDENTIAL_PROXY_HOST")
    port = os.getenv("RESIDENTIAL_PROXY_PORT")

    username = os.getenv("RESIDENTIAL_PROXY_USERNAME")
    password = os.getenv("RESIDENTIAL_PROXY_PASSWORD")

    proxy_url = f'http://customer-{username}:{password}@{host}:{port}'

    proxies = {
        'https': proxy_url
    }

    headers = {
        'x-rapidapi-key': "f2d1322fc9mshd04f3762ac0793ep11069cjsn4e55258922af",
        'x-rapidapi-host': "youtube-media-downloader.p.rapidapi.com"
    }
    querystring = {"videoId": video_id}

    url = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"

    headers = {
        'x-rapidapi-key': "f2d1322fc9mshd04f3762ac0793ep11069cjsn4e55258922af",
        'x-rapidapi-host': "youtube-media-downloader.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring, proxies=proxies, timeout=30)
    
    # Log the response status code and content
    logger.info(f"Response status code: {response.status_code}")
    logger.info(f"Response content: {response.text}")

    try:
        if response.status_code == 200:
            video_url_with_audio = None
            video_data = response.json()
            video_item = video_data.get("videos").get("items")
            for video in video_item:
                print("start with request")
                has_audio = video.get("hasAudio")

                if has_audio:
                    video_url_with_audio = video.get("url")
                    break

            if not video_url_with_audio:
                logger.info("Error: No valid video URL found.")
                return None
            logger.info("Downloading video into memory...")
            # video_response = requests.get(video_url_with_audio, stream=True)
            # if video_response.status_code != 200:
            #     logger.info("Failed to download the video.")
            #     return pytube_download_video(video_url_with_audio)
            # video_buffer = video_response.content
            # logger.info(video_buffer)
            return pytube_download_video(video_url_with_audio, proxies)
        
        return download_youtube_video(youtube_url, proxy_url)

    except (KeyError, IndexError):
        logger.error(f"Error: Unable to fetch video details., {(KeyError, IndexError)} ")
        # return None
    return download_youtube_video(youtube_url, proxy_url)
# Download the video
    # try:
    #     urllib.request.urlretrieve(video_url, output_filename)
    #     logger.info(f"Video downloaded successfully as {output_filename}")
    # except Exception as e:
    #     logger.info(f"Error downloading video: {e}")

# # Example usage:
# youtube_url = "https://www.youtube.com/watch?v=1LzFy7Rr89E"  # Or a Shorts URL
# download_youtube_video(youtube_url)