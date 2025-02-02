from __future__ import annotations

import logging
import os
import re
import uuid
from pathlib import Path

import ffmpeg
import requests
from pydub import AudioSegment
from yt_dlp import YoutubeDL
from utils.settings import BASE_DIR
from pytube import YouTube


DOWNLOAD_FOLDER = BASE_DIR / 'downloads'

logger = logging.getLogger(__name__)


def identify_platform(video_url):
    """
    Identify the platform from the video URL.
    """
    if re.search(r'tiktok.com', video_url):
        return 'tiktok'
    elif re.search(r'youtube.com|youtu.be', video_url):
        return 'youtube'
    elif re.search(r'instagram.com', video_url):
        return 'instagram'
    elif re.search(r'x.com', video_url):
        return 'x'
    elif re.search(r'facebook.com', video_url):
        return 'facebook'
    else:
        return 'website'


def save_video_to_file(video_buffer):
    """
    Save video from a buffer to a temporary file.

    Args:
        video_buffer: The buffer containing the video data.

    Returns:
        The path to the saved video file, or None if an error occurs.
    """

    temp_video_path = os.path.join(DOWNLOAD_FOLDER, F"{uuid.uuid4()}.mp4")
    logger.info(temp_video_path)
    try:
        # Process the video buffer and save it to a file
        process = (
            ffmpeg
            .input('pipe:0')  # Input from stdin (the video buffer)
            .output(temp_video_path, format='mp4', vcodec='libx264', preset='fast')  # Video specs
            .run(input=video_buffer)  # Pass the buffer as input
        )
        logger.info(f"{process}")
        logger.info(f"Video saved successfully to: {temp_video_path}")
        return temp_video_path
    except ffmpeg.Error as e:
        logger.info(f"Error during video saving: {e}")
        return None


def is_audio_valid_pydub(audio_path):
    try:
        audio = AudioSegment.from_file(audio_path)
        if len(audio) > 0:
            logger.info(f"L'audio est valide (durée : {len(audio) / 1000} secondes).")
            return True
        else:
            logger.info("L'audio est vide ou invalide.")
            return False
    except Exception as e:
        logger.info(f"Erreur lors de la vérification de l'audio : {e}")
        return False


def convert_video_to_mp4(input_video_path: str) -> None:
    """
    Convertit une vidéo en MP4 si ce n'est pas déjà le format MP4.
    """
    try:
        output_video_path: str = change_extension_files(input_video_path, new_extension='vide_.mp4')
        print(f"Conversion de {input_video_path} en MP4...")
        ffmpeg.input(input_video_path).output(output_video_path).run()
        print(f"Conversion terminée : {output_video_path}")
        #     deletete the old file

        os.rename(output_video_path, input_video_path)
        # os.remove(output_video_path)
        return input_video_path
    except ffmpeg.Error as e:
        print(f"Erreur lors de la conversion : {e}")
    return None


def change_extension_files(filename, new_extension='.jpg'):
    """
    Change the extension of the given filename to the specified image format.

    Args:
        filename (str): The original filename.
        new_extension (str): The new image extension (default is .jpg).

    Returns:
        str: The filename with the updated extension.
    """
    if not new_extension.startswith('.'):
        new_extension = f".{new_extension}"  # Ensure the extension starts with '.'

    # Use pathlib to handle the filename and extension
    updated_filename = Path(filename).with_suffix(new_extension)
    return str(updated_filename)


def download_youtube_video(youtube_url, proxy_url=None):
    """
    Downloads a YouTube video to the specified full path.

    Args:
        youtube_url (str): The URL of the YouTube video to download.
        full_path (str): The full path, including the filename, where the video will be saved.

    Returns:
        str: The full path of the downloaded video file.
    """
    # Extract the directory from the full path
    output_path =  os.path.join(DOWNLOAD_FOLDER, F"{uuid.uuid4()}.mp4")
    COOKIES_FOLDER = BASE_DIR / 'cookies_files'
    # Ensure the output directory exists
    # os.makedirs(output_path, exist_ok=True)
    cookies_path  =  os.path.join(COOKIES_FOLDER, 'cookies.txt')
    # Specify yt_dlp options
    options = {
        'outtmpl': output_path,  # Full path including filename
        'format': 'best',  # Download the best quality video
        'cookiefile': cookies_path,
        'proxy': proxy_url
    }

    logger.info("Downloading youtube video with YoutubeDL ...")
    try:
        with YoutubeDL(options) as ydl:
            ydl.download([youtube_url])
        print(f"Video downloaded successfully to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def pytube_download_video(download_url, proxies=None):
    try:
        video_title = os.path.join(DOWNLOAD_FOLDER, F"{uuid.uuid4()}.mp4")
        with requests.get(download_url, stream=True, proxies=proxies, timeout=30) as r:
            r.raise_for_status()
            with open(video_title, "wb") as f:
                for chunk in r.iter_content(chunk_size=18192):
                    f.write(chunk)
        print("Video downloaded successfully as:", video_title)
        return video_title
    except Exception as e:
        print("Error during download:", e)
    return None