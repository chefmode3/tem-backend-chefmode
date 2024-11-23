import requests
import urllib.request

from utils.common import save_video_to_file


def download_facebook_video(url, output_filename="downloaded_video.mp4"):
    # API endpoint and headers
    api_url = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"
    headers = {
        "x-rapidapi-key": "1776083f1dmsh864701c7fc5a69dp1d97f3jsn8cb7620cf8c2",
        "x-rapidapi-host": "auto-download-all-in-one.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    # API payload with the Facebook video URL
    payload = {"url": url}

    # Step 2: Make the API request
    response = requests.post(api_url, json=payload, headers=headers)

    # Step 3: Parse the JSON response
    data = response.json()

    # Step 4: Extract the first video URL from "medias"
    try:
        video_url = data['medias'][0]['url']
        print(f"Downloading video from: {video_url}")

    except (KeyError, IndexError):
        print("Error: Could not extract video URL from the response.")
        return

    # Step 5: Download the MP4 video
    try:
        video_response = requests.get(video_url, stream=True)
        if video_response.status_code != 200:
            print("Failed to download the video.")
            return None
        video_buffer = video_response.content
        return save_video_to_file(video_buffer)
    except Exception as e:
        print(f"Error downloading video: {e}")


# # Example usage:
# url = "https://www.facebook.com/share/v/jYJtoPQt17FzDvGj/"
# download_facebook_video(url)
