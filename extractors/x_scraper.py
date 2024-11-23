import requests
import json
import urllib.request
import re

from utils.common import save_video_to_file


def extract_tweet_id(url):
    # Extract the tweet ID from the URL using regex
    match = re.search(r"status/(\d+)", url)
    if match:
        return match.group(1)
    else:
        print("Invalid URL format. Could not extract tweet ID.")
        return None


def download_twitter_video(url, output_filename="downloaded_video.mp4"):
    # Step 1: Extract tweet ID from the URL
    tweet_id = extract_tweet_id(url)
    if not tweet_id:
        return

    # Define the API request details
    api_url = "https://twitter154.p.rapidapi.com/tweet/details"
    headers = {
        "x-rapidapi-key": "1776083f1dmsh864701c7fc5a69dp1d97f3jsn8cb7620cf8c2",
        "x-rapidapi-host": "twitter154.p.rapidapi.com"
    }

    querystring = {"tweet_id": tweet_id}

    # Step 2: Make the API request
    response = requests.get(api_url, headers=headers, params=querystring)

    # Step 3: Parse the JSON response
    data = response.json()

    # Step 4: Extract the video URLs with bitrates
    try:
        video_urls = [
            variant for variant in data['video_url'] if variant['content_type'] == 'video/mp4'
        ]
        # Sort video URLs by bitrate in ascending order
        video_urls_sorted = sorted(video_urls, key=lambda x: x['bitrate'])

        # Check if we have at least two videos with distinct resolutions
        if len(video_urls_sorted) < 2:
            print("Not enough video resolutions available.")
            return

        # Select the second-highest resolution video
        second_highest_resolution_url = video_urls_sorted[-2]['url']
        print(f"Downloading video from: {second_highest_resolution_url}")

    except (KeyError, IndexError):
        print("Error: Could not extract video URL.")
        return

    # Step 5: Download the MP4 video
    try:
        video_response = requests.get(second_highest_resolution_url, stream=True)
        if video_response.status_code != 200:
            print("Failed to download the video.")
            return None
        video_buffer = video_response.content
        return save_video_to_file(video_buffer)
    except Exception as e:
        print(f"Error downloading video: {e}")


# # Example usage:
# url = "https://x.com/Lee_Fabricee/status/1850919444387647949"
# download_twitter_video(url)
