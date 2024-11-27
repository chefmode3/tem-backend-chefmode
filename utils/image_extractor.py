import requests
import time
import os

API_KEY = "oem4iVmwmykgSUyzA3tbGPCmkMgseN8NQUZrCKeLKY"
EXTRACTION_URL = "https://api.extract.pics/v0/extractions"
DOWNLOAD_URL = "https://api.extract.pics/v0/downloads/single"

def download_first_image(target_url, filename="recipe_image.jpg"):
    """Extracts the first image from the target URL and saves it locally."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Start the extraction process
    try:
        response = requests.post(EXTRACTION_URL, headers=headers, json={"url": target_url})
        response_data = response.json()
    except requests.exceptions.RequestException as e:
        logger.info(f"Request error: {e}")
        return False
    except ValueError:
        logger.info("Error: Failed to parse JSON response.")
        logger.info("Response content:", response.content)
        return False

    # Debugging: Print response status code and data
    logger.info(f"Response Status Code: {response.status_code}")
    logger.info(f"Response Data: {response_data}")

    # Check if extraction started successfully
    if not (200 <= response.status_code < 300):
        logger.info(f"Error starting extraction: {response_data.get('message', 'Unknown error')}")
        logger.info("Full response:", response_data)
        return False

    # Ensure 'id' is in response_data['data']
    if "id" not in response_data.get("data", {}):
        logger.info("Error: No extraction ID found in the response.")
        logger.info("Full response:", response_data)
        return False

    extraction_id = response_data["data"]["id"]
    logger.info(f"Extraction started successfully. ID: {extraction_id}")

    # Poll the extraction status every 5 seconds
    url = f"{EXTRACTION_URL}/{extraction_id}"
    while True:
        try:
            status_response = requests.get(url, headers=headers)
            status_data = status_response.json()
        except requests.exceptions.RequestException as e:
            logger.info(f"Request error: {e}")
            return False
        except ValueError:
            logger.info("Error: Failed to parse JSON response.")
            logger.info("Response content:", status_response.content)
            return False

        # Debugging: Print status response
        logger.info(f"Status Response Status Code: {status_response.status_code}")
        logger.info(f"Status Response Data: {status_data}")

        status = status_data["data"]["status"]
        logger.info(f"Current status: {status}")

        if status == "done":
            images = status_data["data"]["images"]
            if not images:
                logger.info("No images found.")
                return False
            image = images[0]  # Get the first image
            # Check if the image has a URL
            if "url" in image:
                break
            else:
                logger.info("Image data is incomplete. Retrying...")
        elif status == "error":
            logger.info("Extraction failed.")
            return False

        logger.info("Extraction pending, retrying in 5 seconds...")
        time.sleep(5)  # Wait 5 seconds before retrying

    # Download the first image using the image URL
    image_url = image["url"]
    try:
        download_response = requests.get(image_url, headers=headers)
    except requests.exceptions.RequestException as e:
        logger.info(f"Request error: {e}")
        return False

    if download_response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(download_response.content)
        logger.info(f"Image saved as {filename}")
        return True
    else:
        logger.info(f"Failed to download image: {download_response.status_code}")
        logger.info("Response content:", download_response.content)
        return False

# Example usage:
download_first_image("https://grandbaby-cakes.com/nashville-hot-chicken/")
