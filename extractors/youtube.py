import os
import uuid

import yt_dlp
import sys
import logging
import random
from datetime import datetime

from extractors import logger
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


def download_youtube_video(url, max_retries=3):
    """Download video with retry logic and proxy rotation"""
    retry_count = 0
    output_path = os.path.join(DOWNLOAD_FOLDER, f"{uuid.uuid4()}.mp4")
    MAX_SIZE_MB = 50

    while retry_count < max_retries:
        # Get a random proxy for this attempt
        proxy = get_random_proxy()

        ydl_opts = {
            'format': '(bestvideo[height=240]/bestvideo[height<=360][height>240])[ext=mp4]+bestaudio[ext=m4a]/(best[height=240]/best[height<=360][height>240])[ext=mp4]',
            'proxy': proxy,
            'logger': MyLogger(),
            'progress_hooks': [my_progress_hook],
            'outtmpl': output_path,
            'ignoreerrors': True,
            'nocheckcertificate': True,
            'verbose': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'socket_timeout': 30,
            'retries': 2,
            'concurrent_fragments': 5,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Vérifier d'abord la taille
                info = ydl.extract_info(url, download=False)

                # Calculer la taille
                size_mb = None
                if 'filesize' in info:
                    size_mb = info['filesize'] / (1024 * 1024)
                else:
                    # Iterate through formats to find a valid size
                    for f in info.get('formats', []):
                        if f.get('filesize'):
                            size_mb = f['filesize'] / (1024 * 1024)
                            break  # Stop searching once a size is found
                        elif f.get('filesize_approx'):
                            size_mb = f['filesize_approx'] / (1024 * 1024)
                            break

                # Vérifier la taille avant de télécharger
                if size_mb is None:
                    logging.error("Impossible de déterminer la taille du fichier")
                    retry_count += 1
                    continue
                elif size_mb > MAX_SIZE_MB:
                    logging.error(f"Fichier trop volumineux ({size_mb:.2f} MB). Maximum autorisé: {MAX_SIZE_MB} MB")
                    return None

                # Si la taille est OK, procéder au téléchargement
                logging.info(f'Attempt {retry_count + 1}/{max_retries} - Starting download for: {url}')
                logging.info(f"Taille du fichier OK ({size_mb:.2f} MB). Démarrage du téléchargement...")

                error_code = ydl.download([url])

                if error_code == 0:
                    logging.info('Download completed successfully')
                    return output_path

                logging.error(f'Download failed with code: {error_code}')
                retry_count += 1

        except Exception as e:
            logging.error(f'Error with proxy {proxy.split("@")[1] if "@" in proxy else proxy}: {str(e)}')
            retry_count += 1
            if retry_count < max_retries:
                logging.info('Retrying with different proxy...')
                continue

    logging.error(f'All {max_retries} attempts failed')
    return None
    
    logging.error(f'All download attempts failed after {max_retries} tries')
    return None
