import http.client
import json
import urllib.request
import re

def extract_video_id(youtube_url):
    # Regular expression to extract the video ID from various YouTube URL formats
    match = re.search(r"(?:v=|\/(vi|v|shorts)\/|\/embed\/|youtu\.be\/)([a-zA-Z0-9_-]{11})", youtube_url)
    if match:
        return match.group(2)
    else:
        print("Error: Unable to extract video ID.")
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

    # Parse the JSON response
    response = json.loads(data.decode("utf-8"))
    print(response)  # Optional: print the full response for debugging

    # Extract the first video URL with audio
    try:
        video_streams = response['videos']['items']
        video_url = video_streams[0].get('url')
    except (KeyError, IndexError):
        print("Error: Video URL not found.")
        return

    # Download the video
    try:
        urllib.request.urlretrieve(video_url, output_filename)
        print(f"Video downloaded successfully as {output_filename}")
    except Exception as e:
        print(f"Error downloading video: {e}")

# # Example usage:
# youtube_url = "https://www.youtube.com/watch?v=1LzFy7Rr89E"  # Or a Shorts URL
# download_youtube_video(youtube_url)
