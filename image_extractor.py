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
        print(f"Request error: {e}")
        return False
    except ValueError:
        print("Error: Failed to parse JSON response.")
        print("Response content:", response.content)
        return False

    # Debugging: Print response status code and data
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Data: {response_data}")

    # Check if extraction started successfully
    if not (200 <= response.status_code < 300):
        print(f"Error starting extraction: {response_data.get('message', 'Unknown error')}")
        print("Full response:", response_data)
        return False

    # Ensure 'id' is in response_data['data']
    if "id" not in response_data.get("data", {}):
        print("Error: No extraction ID found in the response.")
        print("Full response:", response_data)
        return False

    extraction_id = response_data["data"]["id"]
    print(f"Extraction started successfully. ID: {extraction_id}")

    # Poll the extraction status every 5 seconds
    url = f"{EXTRACTION_URL}/{extraction_id}"
    while True:
        try:
            status_response = requests.get(url, headers=headers)
            status_data = status_response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return False
        except ValueError:
            print("Error: Failed to parse JSON response.")
            print("Response content:", status_response.content)
            return False

        # Debugging: Print status response
        print(f"Status Response Status Code: {status_response.status_code}")
        print(f"Status Response Data: {status_data}")

        status = status_data["data"]["status"]
        print(f"Current status: {status}")

        if status == "done":
            images = status_data["data"]["images"]
            if not images:
                print("No images found.")
                return False
            image = images[0]  # Get the first image
            # Check if the image has a URL
            if "url" in image:
                break
            else:
                print("Image data is incomplete. Retrying...")
        elif status == "error":
            print("Extraction failed.")
            return False

        print("Extraction pending, retrying in 5 seconds...")
        time.sleep(5)  # Wait 5 seconds before retrying

    # Download the first image using the image URL
    image_url = image["url"]
    try:
        download_response = requests.get(image_url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return False

    if download_response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(download_response.content)
        print(f"Image saved as {filename}")
        return True
    else:
        print(f"Failed to download image: {download_response.status_code}")
        print("Response content:", download_response.content)
        return False

# Example usage:
download_first_image("https://grandbaby-cakes.com/nashville-hot-chicken/")
