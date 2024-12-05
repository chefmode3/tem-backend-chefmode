from __future__ import annotations

import base64
import logging
import math
import os
import tempfile
import uuid

import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip
from openai import OpenAI
from pydub import AudioSegment

from utils.settings import BASE_DIR

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'), organization=os.environ.get('OPENAI_ORGANIZATION'))


# Function to split video and audio
def split_video_audio(video_path):
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

    base64Frames = []
    for second in range(0, int(video_length_seconds), frame_step):
        video.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
        success, frame = video.read()
        if success:
            base64Frames.append(encode_frame(frame))

    #  Save the final frame as 'recipe_image.jpg' locally
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_count - frame_count)
    success, frame = video.read()

    recipe_img = BASE_DIR / 'downloads' / f'{uuid.uuid4()}_recipe_img.jpg'
    #  change_extension_to_image(video_path)
    if success:
        cv2.imwrite(recipe_img, frame)

    video.release()
    logger.info(f"Number of Frames Captured: {len(base64Frames)}")
    return recipe_img


def process_video(video_path):
    description = ''
    # filename = os.path.basename(video_path)
    logger.info(f"Processing {video_path}...")

    video = VideoFileClip(video_path)
    if not video.audio:
        logger.info('No audio track found in the video.')
        transcript = 'No Transcript available, do not mention this in the final recipe.'
    else:
        video_clip_path, audio_clip_path = split_video_audio(video_path)
        if audio_clip_path:
            transcript = extract_transcript(audio_clip_path)
        else:
            transcript = 'No Transcript available, do not mention this in the final recipe.'

        recipe_img = get_video_frames(video_path)

        PROMPT_MESSAGES = [
                {
                    'role': 'system',
                    'content': (
                        'extract recipe information from video transcripts'
                        'Extract recipe title, servings, total time in hours or minute, ingredients, and directions.'
                        'title_process if available'
                        '2. **Ingredients**: For each ingredient, provide:'
                        '  - `name`: A  names of the ingredient .'
                        '  - `quantity`: A list of floats representing the range or exact quantities (e.g., [40, 50] for "40-50g").'
                        ' - `unit`: The primary unit for the ingredient (e.g., "g", "cups").'
                        '   - `alternative_measurements`: A list of objects where:'
                        '     - Each object contains a `unit` (e.g., "cups", "tbsp").'
                        '     - Each object contains a `quantity` as a list of floats (to support ranges if needed).'

                        '**Example Ingredient**:'
                        'For "40-50g (4 cups 2 tbsp) of bread flour", the JSON structure should look like this:'
                        ' Ensure the response is strictly in JSON format'
                        ' and only follows this structure:'

                        '{ '
                        "  'recipe_information': { "
                        "    'title': 'string', "
                        "    'servings': integer, "
                        "    'preparation_time': 'string', "
                        "    'description': 'string', "
                        "    'image_url': 'string' "
                        '  }, '
                        "  'ingredients': [ "
                        '    { '

                        '      "name": "string" '
                        "      'quantity': List[float], "
                        "      'unit': 'string', "
                        "       'alternative_measurements': ["
                        '     { '
                        '         "unit": "string",'
                        '          "quantity": [float]'
                        '      },'
                        '],'
                        '    } '
                        '  ], '
                        "  'processes': [ "
                        '    { '
                        "      'title_process': 'string', "
                        "      'step_number': integer, "
                        "      'instructions': 'string' "
                        '    } '
                        '  ], '

                        '}'
                        'Do not infer or add any information not explicitly stated.'
                        'only return the result in a json format and not in markdown'
                        "If there is no content to review, do not make up a recipe, instead output this: 'Cannot identify Recipe. Please try again with another link.'"
                        'You will ALWAYS supply ingredient amounts. You will supply EXACTLY what you find in the text.'
                    )
                },
                {'role': 'user', 'content': f"Here is the transcript of the video {transcript}"}
            ]

        params = {
            'model': 'gpt-4o-mini',
            'messages': PROMPT_MESSAGES,
            'max_tokens': 2000,
            'response_format': {'type': 'json_object'}
        }

        result = client.chat.completions.create(**params)
        description = result.choices[0].message.content

    return description, recipe_img
