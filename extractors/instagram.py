from __future__ import annotations

import logging
import os
import re
import uuid

import instaloader
import http.client

import requests
import json
import urllib.request
import re


from utils.common import save_video_to_file, DOWNLOAD_FOLDER

logger = logging.getLogger(__name__)


def download_instagram_video(instagram_url, output_filename="downloaded_video.mp4"):
    # Step 1: Extract the shortcode from the provided Instagram URL
    # Updated regex pattern to include 'reel', 'reels', and 'p'
    match = re.search(r"(?:[^/]+/)?(reels?|p)/([^/?#&]+)", instagram_url)
    output_filename =  os.path.join(DOWNLOAD_FOLDER, F"{uuid.uuid4()}.mp4")
    if not match:
        raise ValueError("Invalid Instagram URL. Could not extract shortcode.")

    shortcode = match.group(2)  # Extract the actual shortcode
    print(f"Extracted shortcode: {shortcode}")

    # Step 2: Make the API request

    conn = http.client.HTTPSConnection("instagram-scraper-api2.p.rapidapi.com")

    # url = "https://instagram-scraper-api2.p.rapidapi.com/v1/post_info"

    # querystring = {"code_or_id_or_url": shortcode, "include_insights": "true"}

    headers = {
        "x-rapidapi-key": "1776083f1dmsh864701c7fc5a69dp1d97f3jsn8cb7620cf8c2",
        "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
    }


    for _ in range(4):
        conn.request("GET", f"/v1/post_info?code_or_id_or_url={shortcode}&include_insights=true", headers=headers)
        res = conn.getresponse()
        data = res.read()

        # Step 3: Parse the JSON response
        response = json.loads(data.decode("utf-8"))

        # Step 4: Extract video URL
        try:
            print(f"Downloading video from: {response['data'].keys()}, re")

            if 'video_versions' in response['data'].keys():
                video_versions = response['data']['video_versions']
                video_url = video_versions[0]['url']
            elif 'carousel_media' in response['data'].keys():
                video_versions = response['data']['carousel_media'][0]['video_versions']
                video_url = video_versions[0]['url']
            else:
                video_url = response['data']['video_url']
                  # Use the first available video URL
            print(f"Downloading video from: {video_url}")
        except Exception as e:
            print(f"Error downloading video: {e}")
            continue

        # Step 5: Download the MP4 video
        try:
            urllib.request.urlretrieve(video_url, output_filename)
            print(f"Video downloaded successfully as {output_filename}")
            return output_filename
        except Exception as e:
            print(f"Error downloading video: {e}")
    return  instagram_video_downloader(instagram_url)


def instagram_video_downloader(instagram_url):
    """
    Download the video from an Instagram URL.
    """
    try:
        logger.info("Downloading Instagram video with instaloader ...")
        # Create an instance of Instaloader
        loader = instaloader.Instaloader()

        # Load the post
        post = instaloader.Post.from_shortcode(loader.context, instagram_url)

        # Get the video URL
        video_url = post.video_url

        # Download the video
        video_buffer = requests.get(video_url).content

        # Save the video to a file
        video_path = save_video_to_file(video_buffer)

        return video_path
    except Exception as e:
        logger.error(f"An error occurred while downloading the Instagram video: {e}")
        return None
