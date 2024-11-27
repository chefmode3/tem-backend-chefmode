from __future__ import annotations

import logging
import os

import boto3
import cv2
import numpy as np
import requests
from botocore.exceptions import NoCredentialsError


# Configuration AWS S3
S3_BUCKET = os.getenv('S3_BUCKET')
S3_REGION = os.getenv('S3_REGION')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
logger = logging.getLogger(__name__)


# Initialise le client S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)


def upload_to_s3(file_path, s3_file_name):
    """
    Upload un fichier local vers un bucket S3.
    :param file_path: Chemin local du fichier.
    :param s3_file_name: Nom de fichier cible sur S3.
    :return: URL publique de l'image sur S3.
    """
    try:
        s3_client.upload_file(
            file_path,
            S3_BUCKET,
            s3_file_name,
            ExtraArgs={'ACL': 'public-read'}
        )
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_file_name}"
        logger.info(f"Fichier uploadé avec succès : {file_url}")
        return file_url
    except NoCredentialsError:
        logger.error("Erreur : Les informations d'identification AWS sont manquantes.")
        return None
    except Exception as e:
        logger.error(f"Erreur pendant l'upload : {e}")
        return None


def load_image_from_url(url):
    """
    Charge une image depuis une URL et la convertit en un tableau NumPy pour OpenCV.
    :param url: URL de l'image.
    :return: Image en format OpenCV (ou None si une erreur survient).
    """
    try:
        # Télécharger l'image
        response = requests.get(url)
        response.raise_for_status()  # Vérifie les erreurs HTTP

        # Convertir les données en tableau NumPy
        image_array = np.frombuffer(response.content, np.uint8)

        # Décoder l'image en format OpenCV
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            logger.error("Erreur : Impossible de décoder l'image.")
            return None
        return image
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors du téléchargement de l'image : {e}")
        return None


def save_image_to_s3_from_url(image_url, s3_file_name):
    """
    Charge une image depuis une URL, la sauvegarde localement, puis l'upload sur S3.
    :param image_url: URL de l'image à télécharger.
    :param s3_file_name: Nom de fichier cible sur S3.
    :return: URL publique de l'image sur S3.
    """
    # Charger l'image depuis l'URL
    image = load_image_from_url(image_url)

    if image is not None:
        # Sauvegarder l'image localement
        local_file_path = 'temp_image.jpg'
        cv2.imwrite(local_file_path, image)
        logger.info(f"Image sauvegardée localement : {local_file_path}")

        # Uploader l'image sur S3
        return upload_to_s3(local_file_path, s3_file_name)
    else:
        logger.info("Échec du chargement de l'image.")
        return None
