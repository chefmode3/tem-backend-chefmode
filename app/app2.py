import streamlit as st
import re
import os
from tiktok import download_tiktok
from new_youtube import download_youtube
from instagram import download_instagram_video
from video_analyzer import process_video
import time
from recipe_extractor_website import scrape_and_analyze_recipe

def main():
    st.title("Cookmode Recipe Extractor")
    st.write("Provide a recipe link from any website or a video link from Instagram, YouTube, or TikTok, and get a concise, no-nonsense recipe.")

    # User inputs the video URL
    video_url = st.text_input("Enter any URL:")

    # Button to start the download process
    if st.button("Get Recipe"):
        with st.spinner('Generating Recipe...'):
            if video_url:
                # Determine the platform and call the appropriate function
                platform = identify_platform(video_url)
                if platform == "tiktok":
                    download_tiktok(video_url)
                    # st.success("TikTok video downloaded successfully!")
                    output_filename = "../downloaded_video.mp4"
                    time.sleep(2)
                    description = process_video(output_filename)
                    st.image("recipe_image.jpg")
                    st.markdown(description, unsafe_allow_html=True)
                elif platform == "youtube":
                    download_youtube(video_url, output_filename="../downloaded_video.mp4")
                    # st.success("YouTube video downloaded successfully!")
                    time.sleep(2)
                    output_filename = "../downloaded_video.mp4"
                    description = process_video(output_filename)
                    st.image("recipe_image.jpg")
                    st.markdown(description, unsafe_allow_html=True)
                elif platform == "instagram":
                    download_instagram_video(video_url)
                    # st.success("Instagram video downloaded successfully!")
                    time.sleep(2)
                    output_filename = "../downloaded_video.mp4"
                    description = process_video(output_filename)
                    st.image("recipe_image.jpg")
                    st.markdown(description, unsafe_allow_html=True)

                elif platform == "website":
                    description, got_image = scrape_and_analyze_recipe(video_url)
                    if got_image:
                        st.image("recipe_image.jpg")
                    else:
                        st.warning("Unable to retrieve image for this recipe.")
                    st.markdown(description)

            else:
                st.warning("Please enter a URL.")

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

if __name__ == "__main__":
    main()