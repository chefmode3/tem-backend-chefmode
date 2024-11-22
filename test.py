import http
import json

import cv2
import ffmpeg
import requests
from pytube import YouTube
# import whisper
import tempfile
import os

from extractors.new_youtube import extract_video_id
from extractors.video_analyzer import extract_transcript


def get_video_stream_url(video_url):
    """
    Utilise Pytube pour extraire l'URL du flux vidéo et audio.
    """
    yt = YouTube(video_url)
    # Sélectionner la meilleure qualité vidéo et audio
    video_stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
    return video_stream.url

def extract_audio_to_tempfile(video_url):
    """
    Download video to buffer, extract audio, and save it to a temporary file.
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        print("Invalid video URL.")
        return None

    # Step 1: Fetch video URL using RapidAPI
    conn = http.client.HTTPSConnection("youtube-media-downloader.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "f2d1322fc9mshd04f3762ac0793ep11069cjsn4e55258922af",
        'x-rapidapi-host': "youtube-media-downloader.p.rapidapi.com"
    }
    conn.request("GET", f"/v2/video/details?videoId={video_id}", headers=headers)
    res = conn.getresponse()
    data = res.read()

    # Parse JSON response
    # response = json.loads(data.decode("utf-8"))
    #
    # try:
    #     video_streams = response['videos']['items']
    #     video_url_with_audio = video_streams[0].get('url')
    #     if not video_url_with_audio:
    #         print("Error: No valid video URL found.")
    #         return None
    # except (KeyError, IndexError):
    #     print("Error: Unable to fetch video details.")
    #     return None
    #
    # # Step 2: Download video into a buffer
    # print("Downloading video into memory...")
    # video_response = requests.get(video_url_with_audio, stream=True)
    # if video_response.status_code != 200:
    #     print("Failed to download the video.")
    #     return None
    # video_buffer = video_response.content
    # print("Video downloaded into memory.")
    #
    # # Step 3: Extract audio to a temporary file
    # temp_audio_path = tempfile.NamedTemporaryFile(delete=True, suffix=".wav").name
    # print(f"Extracting audio to temporary file: {temp_audio_path}")
    #
    # # Use ffmpeg-python to process the video buffer
    # try:
    #     process = (
    #         ffmpeg
    #         .input('pipe:0')  # Input from stdin
    #         .output(temp_audio_path, format='wav', acodec='pcm_s16le', ac=1, ar='16000')  # Audio specs
    #         .run(input=video_buffer)
    #     )
    #     print(f"Audio extracted successfully to: {temp_audio_path}")
    #     return temp_audio_path
    # except ffmpeg.Error as e:
    #     print(f"Error during audio extraction: {e}")
    #     return None


    # return temp_audio_path

# def transcribe_audio_in_real_time(audio_path):
#     """
#     Transcrit l'audio à partir d'un fichier avec Whisper.
#     """
#     model = whisper.load_model("base")
#     print("Transcription en cours...")
#
#     # Transcrire l'audio
#     result = model.transcribe(audio_path)
#     return result["text"]

def read_and_process_stream_with_opencv(video_url):
    """
    Charge un flux vidéo avec OpenCV pour traitement en temps réel
    et affiche la transcription de l'audio.
    """
    print("Téléchargement de l'audio pour transcription...")
    # audio_path = extract_audio_to_tempfile(video_url)

    try:
        audio_path = extract_audio_to_tempfile(video_url)
        # Transcrire l'audio
        transcription = extract_transcript(audio_path)
        print("Transcription :", transcription)

        # # Lire le flux vidéo
        # stream_url = get_video_stream_url(video_url)
        # cap = cv2.VideoCapture(stream_url)
        #
        # if not cap.isOpened():
        #     print("Impossible d'ouvrir le flux vidéo.")
        #     return
        #
        # while True:
        #     ret, frame = cap.read()
        #     if not ret:
        #         print("Fin du flux vidéo.")
        #         break
        #
        #     # Afficher la vidéo avec OpenCV
        #     cv2.imshow("Video Stream", frame)
        #
        #     # Quitter avec la touche 'q'
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break
        #
        # cap.release()
        # cv2.destroyAllWindows()
    finally:
        # Supprimer le fichier audio temporaire
        if os.path.exists(audio_path):
            os.remove(audio_path)

# Exemple d'utilisation
video_url = "https://youtu.be/EYXQmbZNhy8?si=XZTClNZyEluMEJMw"  # Remplacez par une URL valide
read_and_process_stream_with_opencv(video_url)
