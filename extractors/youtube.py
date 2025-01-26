import os
import uuid

import yt_dlp
import sys
import logging
import random
from datetime import datetime

from utils.common import DOWNLOAD_FOLDER

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ytdlp_download.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# List of proxy configurations
PROXIES = [
    "socks5://ashishbishnoi18215139:VGgkmK1dnNHA@x282.fxdx.in:17170",
    "socks5://ashishbishnoi18215006:mG6c01qq55Ll@x282.fxdx.in:17169",
    "socks5://ashishbishnoi18214338:nxTN1usMbqHd@x378.fxdx.in:14896"
]

class MyLogger:
    def debug(self, msg):
        if msg.startswith('[debug] '):
            logging.debug(msg)
        else:
            logging.debug(f'[debug] {msg}')
    
    def info(self, msg):
        logging.info(msg)
    
    def warning(self, msg):
        logging.warning(msg)
    
    def error(self, msg):
        logging.error(msg)

def my_progress_hook(d):
    if d['status'] == 'downloading':
        try:
            progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
            logging.info(f'Downloading... {progress:.1f}% of {d["total_bytes_str"]}')
        except:
            logging.info(f'Downloading... {d.get("downloaded_bytes_str", "N/A")} downloaded')
    elif d['status'] == 'finished':
        logging.info('Download completed. Now converting...')
    elif d['status'] == 'error':
        logging.error(f'Error occurred: {d.get("error")}')

def get_random_proxy():
    """Randomly select a proxy from the list"""
    proxy = random.choice(PROXIES)
    logging.info(f'Selected proxy: {proxy.split("@")[1]}')  # Log only the host:port part for security
    return proxy

def download_youtube_video(url,  max_retries=4):
    """Download video with retry logic and proxy rotation"""
    retry_count = 0
    output_path =  os.path.join(DOWNLOAD_FOLDER, F"{uuid.uuid4()}.mp4")
    while retry_count < max_retries:
        # Get a random proxy for this attempt
        proxy = get_random_proxy()
        
        ydl_opts = {
            # Best video (mp4) + best audio
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            
            # Proxy settings
            'proxy': proxy,
            
            # Progress and logging
            'logger': MyLogger(),
            'progress_hooks': [my_progress_hook],
            
            # Output template
            'outtmpl': '%(title)s-%(id)s.%(ext)s' if not output_path else output_path,
            
            # Other options
            'ignoreerrors': True,  # Continue on download errors
            'nocheckcertificate': True,  # Ignore HTTPS certificate validation
            'verbose': True,
            
            # Post-processing
            'postprocessors': [{
                # Merge video and audio
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            
            # Network settings
            'socket_timeout': 30,  # Timeout for socket operations
            'retries': 5,  # Number of retries for failed downloads per proxy
            
            # Fragment downloads
            'concurrent_fragments': 5,  # Number of fragments to download concurrently
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logging.info(f'Attempt {retry_count + 1}/{max_retries} - Starting download for: {url}')
                error_code = ydl.download([url])
                
                if error_code == 0:
                    logging.info('Download completed successfully')
                    return output_path
                else:
                    logging.error(f'Download failed with code: {error_code}')
                    retry_count += 1
                    
        except Exception as e:
            logging.error(f'Error with proxy {proxy.split("@")[1]}: {str(e)}')
            retry_count += 1
            if retry_count < max_retries:
                logging.info(f'Retrying with different proxy...')
                continue
    
    logging.error(f'All download attempts failed after {max_retries} tries')
    return None
