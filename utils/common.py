import re


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
    elif re.search(r"x.com", video_url):
        return "x"
    elif re.search(r"facebook.com", video_url):
        return "facebook"
    else:
        return "website"
