import re
from extractors.tiktok import download_tiktok
from extractors.new_youtube import download_youtube
from extractors.instagram import download_instagram_video
from extractors.video_analyzer import process_video
import time
from extractors.recipe_extractor_website import scrape_and_analyze_recipe
from utils.common import identify_platform


def fetch_description(request_data):
    video_url = request_data["video_url"]
    platform = identify_platform(video_url)

    final_content = None
    if platform == "tiktok":
        download_tiktok(video_url)
        # st.success("TikTok video downloaded successfully!")
        output_filename = "downloaded_video.mp4"
        time.sleep(2)
        final_content = process_video(output_filename)
        # st.image("recipe_image.jpg")
        # st.markdown(description, unsafe_allow_html=True)
    elif platform == "youtube":
        download_youtube(video_url, output_filename="downloaded_video.mp4")
        # st.success("YouTube video downloaded successfully!")
        time.sleep(2)
        output_filename = "downloaded_video.mp4"
        final_content = process_video(output_filename)
        # st.image("recipe_image.jpg")
        # st.markdown(description, unsafe_allow_html=True)
    elif platform == "instagram":
        download_instagram_video(video_url)
        # st.success("Instagram video downloaded successfully!")
        time.sleep(2)
        output_filename = "downloaded_video.mp4"
        final_content = process_video(output_filename)
        # st.image("recipe_image.jpg")
        # st.markdown(description, unsafe_allow_html=True)

    elif platform == "website":
        description, got_image = scrape_and_analyze_recipe(video_url)
        final_content = description
    return final_content
