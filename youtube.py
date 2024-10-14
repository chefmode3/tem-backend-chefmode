from pytubefix import YouTube

def download_youtube(url):
    vid = YouTube(url)

    video_download = vid.streams.get_highest_resolution()
    audio_download = vid.streams.get_audio_only()

    entry = YouTube(url).title

    print(f"\nVideo found: {entry}\n")

    print(f"Downloading Video...")
    video_download.download(filename=f"downloaded_video.mp4")

    print("Program Completed")