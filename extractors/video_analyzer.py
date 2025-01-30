from __future__ import annotations

import base64
import logging
import math
import os
import tempfile
import uuid

import cv2
from openai import OpenAI
from pydub import AudioSegment

from extractors.recipe_extractor_website import group_markdown_to_json
from utils.settings import BASE_DIR

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'), organization=os.environ.get('OPENAI_ORGANIZATION'))


# Function to split video and audio
def split_video_audio(video_path):
    # Use pydub to extract and reduce the quality of the audio file

    try:
        # Use pydub to extract and reduce the quality of the audio file
        audio = AudioSegment.from_file(video_path)
        reduced_audio = audio.set_frame_rate(22050).set_channels(1).set_sample_width(2)  # Reduce quality

        audio_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        reduced_audio.export(audio_temp_file.name, format='mp3', bitrate='32k')  # Export as mp3

        return video_path, audio_temp_file.name
    except Exception as e:
        logger.error(f"An error occurred while splitting video and audio: {e}")
        return None, None


# Function to extract transcript using OpenAI Whisper
def extract_transcript(audio_file_path):
    try:
        with open(audio_file_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model='whisper-1',
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        logger.error(f"An error occurred while extracting the transcript: {e}")
        return None


# Function to calculate frame step
def calculate_frame_step(video_length_seconds, max_frames=60):
    if video_length_seconds < max_frames:
        return 1
    else:
        return max(1, math.ceil(video_length_seconds / max_frames))


# Function to encode frame
def encode_frame(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')


# Function to get video frames as base64
def get_video_frames(video_path):
    video = cv2.VideoCapture(video_path)
    frame_rate = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    video_length_seconds = frame_count / frame_rate

    frame_step = calculate_frame_step(video_length_seconds)

    logger.info(f"Video Frame Rate: {frame_rate}")
    logger.info(f"Total Frame Count: {frame_count}")
    logger.info(f"Video Length (seconds): {video_length_seconds}")
    logger.info(f"Calculated Frame Step: {frame_step}")
    #  Save the final frame as 'recipe_image.jpg' locally
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_count - frame_count)
    success, frame_img = video.read()

    recipe_img = BASE_DIR / 'downloads' / f'{uuid.uuid4()}_recipe_img.jpg'
    base64Frames = []
    for second in range(0, int(video_length_seconds), frame_step):
        video.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
        success, frame = video.read()
        if success:
            base64Frames.append(encode_frame(frame))

    #  change_extension_to_image(video_path)
    if success:
        cv2.imwrite(recipe_img, frame_img)

    video.release()
    logger.info(f"Number of Frames Captured: {len(base64Frames)}")
    return recipe_img, base64Frames


def has_audio(video_path: str) -> bool:
    """
    Check for audio using pydub.
    Good for audio processing but requires FFmpeg.

    Args:
        video_path: Path to the video file

    Returns:
        bool: True if video has audio, False otherwise
    """
    try:
        audio = AudioSegment.from_file(video_path)
        return len(audio) > 0
    except Exception as e:
        print(f"Pydub Error: {str(e)}")
        return False


# def has_audio(video_path):
#     try:
#         # Open the video file
#         video = cv2.VideoCapture(video_path)
#         # Get audio channel count (if 0, no audio is present)
#         audio_channels = int(video.get(cv2.CAP_PROP_AUDIO_BASE_INDEX))
#         return audio_channels > 0
#     except Exception as e:
#         print(f"Error: {e}")
#         return False


def process_video(video_path):
    try:
        description = ''
        # filename = os.path.basename(video_path)
        logger.info(f"Processing {video_path}...")
        # recipe_img = ''
        # video = VideoFileClip(video_path)

        if not has_audio(video_path):
            logger.info('No audio track found in the video.')
            transcript = 'No Transcript available, do not mention this in the final recipe.'
        else:
            video_clip_path, audio_clip_path = split_video_audio(video_path)
            logger.info('{} and audio {}'.format(video_clip_path, audio_clip_path))
            # print(video_path, audio_clip_path)
            if audio_clip_path:
                transcript = extract_transcript(audio_clip_path)
            else:
                transcript = 'No Transcript available, do not mention this in the final recipe.'

        recipe_img, base_64_frames = get_video_frames(video_path)
        logger.info('{} and audio \n and transcript '.format( transcript))
        prompt_messages = [
            {
                "role": "user",
                "content": [
                    f"You are a video recipe summarizer. "
                    f"You get information from the video: recipe title, servings, total time, ingredients, directions. You will output in simple, clear markdown. Never output a '''markdown identifier before you begin, just the pure formatting. You will ALWAYS supply ingredient amounts."
                    f"Here is a full transcript of the video: {transcript}.\n"
                    "If there is no content to review, do not make up a recipe, instead output this: 'Cannot identify Recipe. Please try again with another link.'"
                    "These are descriptions of some of the frames from the video. Make sure to analyze the transcript and the frames holistically.",
                    *map(lambda x: {"type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{x}", "detail": "low"}},
                         base_64_frames),
                ],
            },
        ]

        params = {
            'model': 'gpt-4o-mini',
            'messages': prompt_messages,
            'max_tokens': 2000,
        }

        result = client.chat.completions.create(**params)
        description = result.choices[0].message.content
        description_1 = result.choices[0].message.content
        logger.info(description)
        logger.error(description_1)
        recipe_info = group_markdown_to_json(description)
        return recipe_info, recipe_img
    except Exception as err:
        logger.error(f"An error occurred while processing the video: {err}")
        return None, None