from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

from flask import Flask, request
import re
from tiktok import download_tiktok
from new_youtube import download_youtube
from instagram import download_instagram_video
from video_analyzer import process_video
import time
from recipe_extractor_website import scrape_and_analyze_recipe

app = Flask(__name__)


def identify_platform(video_url):
    """
    Identify the platform from the video URL.
    """
    if re.search(r"tiktok.com", video_url):
        return "tiktok"
    elif re.search(r"youtube.com|youtu.be", video_url):
        return "youtube"
    elif re.search(r"instagram.com", video_url):
        return "instagram"
    else:
        return "website"


@app.route("/get/recipe", methods=['GET'])
def image_extractor():
    data = request.json
    video_url = data['video_url']
    # Determine the platform and call the appropriate function
    platform = identify_platform(video_url)
    final_content = None
    if platform == "tiktok":
        download_tiktok(video_url)
        # st.success("TikTok video downloaded successfully!")
        output_filename = "../downloaded_video.mp4"
        time.sleep(2)
        final_content = process_video(output_filename)
        # st.image("recipe_image.jpg")
        # st.markdown(description, unsafe_allow_html=True)
    elif platform == "youtube":
        download_youtube(video_url, output_filename="../downloaded_video.mp4")
        # st.success("YouTube video downloaded successfully!")
        time.sleep(2)
        output_filename = "../downloaded_video.mp4"
        final_content = process_video(output_filename)
        # st.image("recipe_image.jpg")
        # st.markdown(description, unsafe_allow_html=True)
    elif platform == "instagram":
        download_instagram_video(video_url)
        # st.success("Instagram video downloaded successfully!")
        time.sleep(2)
        output_filename = "../downloaded_video.mp4"
        final_content = process_video(output_filename)
        # st.image("recipe_image.jpg")
        # st.markdown(description, unsafe_allow_html=True)

    elif platform == "website":
        description, got_image = scrape_and_analyze_recipe(video_url)
        if got_image:
            final_content = description
    return {
        "content": final_content,
    }


# Run Server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
