import extractors.pyktok2 as pyk


# Function to download the TikTok video
def download_tiktok(video_url, browser='chrome'):
    try:
        print(f"Downloading video from: {video_url}")
        video_info = pyk.get_tiktok(video_url)
        direct_link = video_info["video_url"]
        print("Video downloaded successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

# # Replace this with the URL of the TikTok video you want to download
# video_url = 'https://www.tiktok.com/@tiktok/video/7106594312292453675?is_copy_url=1&is_from_webapp=v1'
#
# # Call the function to download the video
# download_tiktok(video_url)
