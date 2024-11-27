import logging

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from PIL import Image
from io import BytesIO
import os
import random
import time
import tiktoken  # Import tiktoken

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), organization=os.environ.get('OPENAI_ORGANIZATION'))


def extract_main_image(soup):
    """
    Attempt to extract the main image from a given soup object.
    """
    image = soup.find('meta', property='og:image')
    if image and 'content' in image.attrs:
        return image['content']
    image_tags = soup.find_all('img', src=True)  # Fallback for cases where no og:image
    if image_tags:
        logger.info(image_tags)
        return image_tags[0]['src']
    return None


def get_website_content(url):
    """
    Function to handle website requests with retries for handling 403 errors.
    """
    headers_list = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                          " (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        },
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        },
        {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        },
    ]
    for _ in range(5):  # Retry up to 5 times
        headers = random.choice(headers_list)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                time.sleep(random.uniform(1, 3))  # Random sleep to avoid being blocked
                continue
            else:
                raise e
    raise requests.exceptions.RequestException("Failed to retrieve the website after multiple attempts.")


def get_image_with_retry(image_url, retries=5):
    """
    Function to fetch an image with retry logic.
    """
    for _ in range(retries):
        try:
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            return Image.open(BytesIO(img_response.content))
        except requests.exceptions.RequestException:
            time.sleep(random.uniform(1, 3))  # Random sleep to avoid being blocked
            continue
    return None


def tokenize_text(text):
    """
    Tokenize the given text using tiktoken and return the token count.
    """
    encoding = tiktoken.get_encoding("cl100k_base")  # Use the GPT-4 tokenizer
    tokens = encoding.encode(text)
    return len(tokens), tokens


def save_image_locally(image, filename='recipe_image.jpg'):
    """Save the image object to the local environment."""
    try:
        image.save(filename)  # Save the image as a JPEG
        logger.info(f"Image saved successfully as {filename}.")
    except Exception as e:
        logger.error(f"Error saving the image: {e}")


def scrape_and_analyze_recipe(url):
    # Make a request to the given URL with retries and user-agent spoofing
    start = time.time()
    response = get_website_content(url)
    end = time.time()
    logger.info(f"get_website_content took {end - start} seconds")

    # Parse the HTML content
    start = time.time()
    soup = BeautifulSoup(response.text, 'html.parser')
    end = time.time()
    logger.info(f"parsing html took {end - start} seconds")

    # Extract title and body content from HTML
    title = soup.title.string if soup.title else "No title found"

    start = time.time()

    # Extraire le contenu du corps de la page
    body = soup.find('body')

    # Extraire toutes les balises <img> à l'intérieur du corps

    # Extraire le texte de différentes balises à l'intérieur du corps
    text_elements = body.find_all(['p', 'div', 'span', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'])
    body_content = " ".join(
        element.get_text(separator=" ", strip=True)
        for element in text_elements
    )

    end = time.time()
    logger.info(f"Extract all text content took {end - start} seconds")
    # logger.info(body_content)

    start = time.time()
    # Tokenize the body content and logger.info token count
    token_count, tokens = tokenize_text(body_content)
    # logger.info(f"Token Count: {token_count}")
    end = time.time()
    logger.info(f"Tokenize text content took {end - start} seconds")

    start = time.time()
    # Extract main image
    main_image_url = extract_main_image(soup)
    end = time.time()
    logger.info(f"Main Image extraction took {end - start} seconds")

    got_image = False

    # Display the main image if found
    if not main_image_url:
        #     if not re.match(r'^https?:', main_image_url):
        #         main_image_url = requests.compat.urljoin(url, main_image_url)
        #     image = get_image_with_retry(main_image_url)
        #     if image:
        #         save_image_locally(image, 'recipe_image.jpg')  # Save the image locally
        #         got_image = True
        #     else:
        #         logger.info("Failed to retrieve the main image after multiple attempts.")
        #         got_image = False
        # else:
        # images = body.find_all('img')
        # main_image_url = [img.get('src') for img in images if img.get('src')][0]
        logger.info("No main image found.")

    start = time.time()
    # Use OpenAI to analyze the recipe content
    ai_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a culinary and nutrition expert. Your task is to extract recipe information from websites "
                    "and calculate "
                    "nutritional values based on the provided details. Ensure the response is strictly in JSON format"
                    " and follows this structure:"

                    "{ "
                    "  'recipe_information': { "
                    "    'title': 'string', "
                    "    'servings': integer, "
                    "    'preparation_time': integer, "
                    "    'description': 'string', "
                    "    'image_url': 'string' "
                    "  }, "
                    "  'ingredients': [ "
                    "    { "
                    "      'name': 'string', "
                    "      'quantity': float, "
                    "      'unit': 'string', "
                    "    } "
                    "  ], "
                    "  'processes': [ "
                    "    { "
                    "      'step_number': integer, "
                    "      'instructions': 'string' "
                    "    } "
                    "  ], "
                    "  'nutrition': ["
                    "    {"
                    "      'name': 'string',"
                    "      'quantity': float,"
                    "      'unit': 'string'"
                    "    }"
                    "  ]"
                    "}"
                    "Guidelines:"
                    "1. All numerical values must be numbers, not text."
                    "2. Ingredients must always include a 'quantity' and 'unit' when available."
                    "3. Processes must be sequentially numbered starting from 1."
                    "4. Nutritional information must include commonly available nutrients like calories, proteins, "
                    "carbohydrates, fats, fiber, sugar, and sodium. Include as many as possible based on the "
                    "data provided."
                    "5. Ensure the output is **exactly** in JSON format with no additional explanations, "
                    "comments, or headers."
                    "6. Always use the exact ingredient amounts and details as found in the input text."
                    "7. Do not nest objects under the `recipe_information`, `ingredients`, or `processes`. "
                    "Flatten the structure for clarity."
                    "8. Provide the output only as a JSON object without any extra descriptive text."
                    "Return only the JSON output as specified above."
                )
            },
            {
                "role": "user", "content": f"Title: {title}\nURL: {url}"
            }
        ]
    )

    end = time.time()
    logger.info(f"OpenAI took {end - start} seconds")

    recipe_info = ai_response.choices[0].message.content

    return recipe_info, got_image, main_image_url
