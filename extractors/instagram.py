from __future__ import annotations

import logging
import re

import instaloader
import requests

from utils.common import save_video_to_file

logger = logging.getLogger(__name__)


def download_instagram_video(instagram_url, output_filename='downloaded_video.mp4'):
    # Step 1: Extract the shortcode from the provided Instagram URL
    match = re.search(r'(?:reels?|p)/([^/?#&]+)', instagram_url)
    # Initialize Instaloader
    loader = instaloader.Instaloader()
    loader.download_videos = False  # Ensures we don't use default video download
    loader.download_comments = False
    loader.save_metadata = False
    if not match:
        raise ValueError('Invalid Instagram URL. Could not extract shortcode.')

    shortcode = match.group(1)  # Extract the actual shortcode
    logger.info(f"Extracted shortcode: {shortcode}")

    # Step 4: Extract video URL
    try:
        # Load post metadata
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # Check if the post contains a video
        if post.is_video:
            video_url = post.video_url
            print(f"Video URL: {video_url}")

            # Download the video
            # Step 5: Download the MP4 video

            video_response = requests.get(video_url, stream=True)
            if video_response.status_code != 200:
                logger.info('Failed to download the video.')
                return None
            video_buffer = video_response.content
            return save_video_to_file(video_buffer)
    except (KeyError, IndexError):
        logger.info('Error: Could not extract video URL.')
        return
    except Exception as e:
        logger.info(f"Error downloading video: {e}")
