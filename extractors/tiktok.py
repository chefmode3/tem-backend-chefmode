import logging

import extractors.pyktok2 as pyk
from utils.common import save_video_to_file

logger = logging.getLogger(__name__)


# Function to download the TikTok video
def download_tiktok(video_url, browser='chrome'):
    try:
        logger.info(f"Downloading video from: {video_url}")
        video_url_with_audio = pyk.save_tiktok(
            video_url,
            save_video=True,   # Download only the video (no metadata)
            metadata_fn=None,  # Skip metadata storage
        )
        video_buffer = video_url_with_audio.content
        # logger.info(video_buffer)
        return save_video_to_file(video_buffer)
    except Exception as e:
        logger.error(f"An error occurred: {e}")

# # Replace this with the URL of the TikTok video you want to download
# video_url = 'https://www.tiktok.com/@tiktok/video/7106594312292453675?is_copy_url=1&is_from_webapp=v1'
#
# # Call the function to download the video
# download_tiktok(video_url)
