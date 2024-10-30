import os
import cv2
import base64
import math
import json
import tempfile
from pydub import AudioSegment
from openai import OpenAI
import concurrent.futures

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to split video and audio
def split_video_audio(video_path):
    try:
        # Use pydub to extract and reduce the quality of the audio file
        audio = AudioSegment.from_file(video_path)
        reduced_audio = audio.set_frame_rate(22050).set_channels(1).set_sample_width(2)  # Reduce quality

        audio_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        reduced_audio.export(audio_temp_file.name, format="mp3", bitrate="32k")  # Export as mp3

        return video_path, audio_temp_file.name
    except Exception as e:
        print(f"An error occurred while splitting video and audio: {e}")
        return None, None

# Function to extract transcript using OpenAI Whisper
def extract_transcript(audio_file_path):
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        print(f"An error occurred while extracting the transcript: {e}")
        return None

# Function to calculate frame step
def calculate_frame_step(video_length_seconds, max_frames=60):
    if video_length_seconds < max_frames:
        return 1
    else:
        return max(1, math.ceil(video_length_seconds / max_frames))

# Function to encode frame
def encode_frame(frame):
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")

# Function to get video frames as base64
def get_video_frames(video_path):
    video = cv2.VideoCapture(video_path)
    frame_rate = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    video_length_seconds = frame_count / frame_rate

    frame_step = calculate_frame_step(video_length_seconds)

    print(f"Video Frame Rate: {frame_rate}")
    print(f"Total Frame Count: {frame_count}")
    print(f"Video Length (seconds): {video_length_seconds}")
    print(f"Calculated Frame Step: {frame_step}")

    base64Frames = []
    for second in range(0, int(video_length_seconds), frame_step):
        video.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
        success, frame = video.read()
        if success:
            base64Frames.append(encode_frame(frame))

    # Save the final frame as 'recipe_image.jpg' locally
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_count - frame_count)
    success, frame = video.read()
    if success:
        cv2.imwrite('recipe_image.jpg', frame)

    video.release()
    print(f"Number of Frames Captured: {len(base64Frames)}")
    return base64Frames

def process_video(video_path):
    description = ""
    filename = os.path.basename(video_path)
    print(f"Processing {video_path}...")

    video_clip_path, audio_clip_path = split_video_audio(video_path)

    if audio_clip_path:
        transcript = extract_transcript(audio_clip_path)

        if transcript:
            base64Frames = get_video_frames(video_clip_path)

            # Prepare the prompt for GPT-4
            PROMPT_MESSAGES = [
                {
                    "role": "user",
                    "content": [
                        f"You are a video recipe summarizer. "
                        f"You get information from the video: recipe title, servings, total time, ingredients, directions. You will output in simple, clear markdown. Never output a '''markdown identifier before you begin, just the pure formatting. You will ALWAYS supply ingredient amounts."
                        f"Here is a full transcript of the video: {transcript}.\n"
                        "These are descriptions of some of the frames from the video. Make sure to analyze the transcript and the frames holistically.",
                        *map(lambda x: {"type": "image_url",
                                        "image_url": {"url": f"data:image/jpeg;base64,{x}", "detail": "low"}},
                             base64Frames),
                    ],
                },
            ]

            # Define parameters for the API request
            params = {
                "model": "gpt-4o-mini",
                "messages": PROMPT_MESSAGES,
                "max_tokens": 2000,
            }

            # Send the request to GPT-4
            result = client.chat.completions.create(**params)
            description = result.choices[0].message.content

    return description
