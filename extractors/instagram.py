from instagrapi import Client
import os
from pathlib import Path
import random
import time

from utils.common import DOWNLOAD_FOLDER


def setup_client() -> Client:
    """
    Set up Instagram client with proxy settings.
    """
    cl = Client()
    
    try:
        before_ip = cl._send_public_request("https://api.ipify.org/")
        cl.set_proxy("http://ashishbishnoi18:DW2GTLWb8gzyOQDj@proxy.packetstream.io:31112")
        after_ip = cl._send_public_request("https://api.ipify.org/")
        
        print(f"IP Before proxy: {before_ip}")
        print(f"IP After proxy: {after_ip}")
        
        return cl
    except Exception as e:
        print(f"Error setting up client: {str(e)}")
        raise

def add_random_delay():
    """
    Add a random delay between 1-3 seconds between operations
    """
    delay = random.uniform(1, 3)
    time.sleep(delay)

def get_video_url(media_info):
    """
    Extract video URL from media info, handling both direct videos and resources.
    """
    # First check if there's a direct video_url
    if media_info.video_url:
        return media_info.video_url
    
    # If no direct video_url, check resources
    if hasattr(media_info, 'resources') and media_info.resources:
        # Look for the first resource that has a video_url
        for resource in media_info.resources:
            if resource.video_url:
                return resource.video_url
    
    raise Exception("No video URL found in media info or resources")

def download_instagram_video(url: str, retry_count: int = 0) -> str:
    """
    Download an Instagram reel with retry mechanism.
    
    Args:
        url (str): The Instagram reel URL
        cl (Client): Instagram client with proxy configured
        download_folder (str): The folder where the video will be saved
        retry_count (int): Current retry attempt number
    
    Returns:
        Path: The path to the downloaded video file
    """
    url = url.strip()
    cl = setup_client()
    download_folder = DOWNLOAD_FOLDER
    MAX_RETRIES = 6
    try:
        # Extract media PK from URL
        media_pk = cl.media_pk_from_url(url)
        add_random_delay()
        
        # Get media info and extract video URL
        media_info = cl.media_info_a1(media_pk)
        video_url = get_video_url(media_info)
        add_random_delay()
        
        # Create downloads folder if it doesn't exist
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        
        # Download the video
        downloaded_path_ = cl.clip_download_by_url(video_url, folder=download_folder)
        add_random_delay()
        
        print(f"Video downloaded successfully to: {downloaded_path_}")
        return downloaded_path_
        
    except Exception as e:
        if retry_count < MAX_RETRIES - 1:
            retry_count += 1
            print(f"Download failed. Retrying ({retry_count}/{MAX_RETRIES-1})...")
            
            # Create new client for retry
            # new_cl = setup_client()
            return download_instagram_video(url, retry_count)
        else:
            print(f"Error downloading video after {MAX_RETRIES} attempts: {str(e)}")
            raise

#
# if __name__ == "__main__":
#     try:
#         # Get input for URL
#         url = input("Enter Instagram reel URL: ")
#
#         if not url:
#             print("No URL provided. Exiting...")
#             exit()
#
#         # Get download folder
#         download_folder = input("Enter download folder path (press Enter for default 'Downloads'): ")
#
#         # Use default folder if no input provided
#         if not download_folder:
#             download_folder = 'Downloads'
#
#         # Initialize client and try to download
#
#         try:
#             downloaded_path = download_instagram_video(url.strip(), cl, download_folder)
#             print("\nDownload Summary:")
#             print("Status: Success")
#             print(f"File: {downloaded_path}")
#         except Exception as e:
#             print("\nDownload Summary:")
#             print("Status: Failed")
#             print(f"Error: {str(e)}")
#
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")