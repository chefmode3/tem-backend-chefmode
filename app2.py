import streamlit as st
import re
import os
from tiktok import download_tiktok
from youtube import download_youtube
from instagram import download_instagram_video
from video_analyzer import process_video
import time

def main():
    st.title("Video to Recipe")
    st.write("Provide a video recipe link from Instagram, YouTube, or TikTok, and get a concise, no-nonsense recipe.")

    # User inputs the video URL
    video_url = st.text_input("Enter the video URL:")

    # Button to start the download process
    if st.button("Get Recipe"):
        with st.spinner('Generating Recipe...'):
            if video_url:
                # Determine the platform and call the appropriate function
                platform = identify_platform(video_url)
                if platform == "tiktok":
                    download_tiktok(video_url)
                    # st.success("TikTok video downloaded successfully!")
                    output_filename = "downloaded_video.mp4"
                    time.sleep(2)
                elif platform == "youtube":
                    download_youtube(video_url)
                    # st.success("YouTube video downloaded successfully!")
                    time.sleep(2)
                    output_filename = "downloaded_video.mp4"
                elif platform == "instagram":
                    download_instagram_video(video_url)
                    # st.success("Instagram video downloaded successfully!")
                    time.sleep(2)
                    output_filename = "downloaded_video.mp4"
                else:
                    st.error("Unsupported video link. Please provide a valid Instagram, YouTube, or TikTok link.")
                    return

                description = process_video(output_filename)
                st.markdown(description, unsafe_allow_html=True)
            else:
                st.warning("Please enter a video URL.")

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
        return None

if __name__ == "__main__":
    main()