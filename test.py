import cv2
from pytube import YouTube
# import whisper
import tempfile
import os

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
    Extrait l'audio d'une vidéo YouTube et le sauvegarde temporairement.
    """
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_url = audio_stream.url

    temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name

    # Télécharger l'audio
    os.system(f"ffmpeg -i {audio_url} -q:a 0 -map a {temp_audio_path}")

    return temp_audio_path

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
    audio_path = extract_audio_to_tempfile(video_url)

    try:
        audio_path = extract_audio_to_tempfile(video_url)
        # Transcrire l'audio
        # transcription = transcribe_audio_in_real_time(audio_path)
        # print("Transcription :", transcription)

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
