from __future__ import annotations

import logging
import os
import random
import time
import uuid
from io import BytesIO

import requests
import tiktoken  # Import tiktoken
from bs4 import BeautifulSoup
from openai import OpenAI
from PIL import Image

from app.utils.s3_storage import save_image_to_s3_from_url

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'), organization=os.environ.get('OPENAI_ORGANIZATION'))


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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        },
        {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        },
        {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
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
    raise requests.exceptions.RequestException('Failed to retrieve the website after multiple attempts.')


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
    encoding = tiktoken.get_encoding('cl100k_base')  # Use the GPT-4 tokenizer
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
    try:
        # Fetch website content
        start = time.time()
        response = get_website_content(url)
        response.raise_for_status()
        end = time.time()
        logger.error(f"get_website_content took {end - start} seconds")
    except Exception as e:
        logger.error(f"Failed to fetch content: {e}")
        return None, False, None

    # Parse HTML
    try:
        start = time.time()
        soup = BeautifulSoup(response.text, 'html.parser')
        end = time.time()
        logger.error(f"parsing html took {end - start} seconds")
    except Exception as e:
        logger.error(f"HTML parsing error: {e}")
        return None, False, None

    # Extract title
    title = soup.title.string if soup.title else 'No title found'

    # Extract text content
    start = time.time()
    body_content = ' '.join(
        element.get_text(separator=' ', strip=True)
        for element in soup.find_all(['p', 'div', 'span', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'])
    )
    end = time.time()
    logger.error(f"Extract all text content took {end - start} seconds")

    # Tokenize text
    start = time.time()
    token_count, tokens = tokenize_text(body_content)
    end = time.time()
    logger.error(f"Tokenize text content took {end - start} seconds")

    # Extract main image
    main_image_url = extract_main_image(soup)
    got_image = bool(main_image_url)

    # Analyze content using AI
    try:
        start = time.time()
        ai_response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'Extract recipe title, servings, total time in hours or minute, ingredients, and directions.'
                        'title_process if available'
                        ' Ensure the response is strictly in JSON format'
                        ' and only follows this structure:'

                        '{ '
                        "  'recipe_information': { "
                        "    'title': 'string', "
                        "    'servings': integer, "
                        "    'preparation_time': 'string', "
                        "    'description': 'string', "
                        '  }, '
                        "  'ingredients': [ "
                        '    { '

                        '      "full_origin_name_with_quantity": "string" '
                        "      'quantity': float, "
                        "      'unit': 'string', "
                        '    } '
                        '  ], '
                        "  'processes': [ "
                        '    { '
                        "      'title_process': 'string', "
                        "      'step_number': integer, "
                        "      'instructions': 'string' "
                        '    } '
                        '  ], '

                        '}'
                        'Do not infer or add any information not explicitly stated.'
                            'only return the result in a json format and not in markdown'
                            "If there is no content to review, do not make up a recipe, instead output this: 'Cannot identify Recipe. Please try again with another link.'"
                            'You will ALWAYS supply ingredient amounts. You will supply EXACTLY what you find in the text.'
                        )
                },
                {'role': 'user', 'content': f"Title: {title}\nURL: {url}\n\n{body_content}"}
            ]
        )
        end = time.time()
        logger.error(f"OpenAI took {end - start} seconds")

        recipe_info = ai_response.choices[0].message.content
        logger.error(recipe_info)
        s3_file_name = f'{uuid.uuid4()}_image.jpg'
        s3_url = save_image_to_s3_from_url(main_image_url, s3_file_name)
        logger.info(f"s3_image: {s3_url}")
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        recipe_info = None

    return recipe_info, got_image, main_image_url


def analyse_nutritions_base_ingredient(ingredient):
    try:
        start = time.time()
        ai_response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'calculate the nutritional information based on the provided details.  '
                        ' Ensure the response returned is strictly in JSON format and follows this exact structure:  '
                        'only return the result in a json format and not in markdown'
                        "  'nutritions': [ "
                        '    { '
                        '      "name": "string" '
                        "      'quantity': float, "
                        "      'unit': 'string', "
                        '    } '
                        '  ], '
                        )
                },
                {'role': 'user', 'content': f"Here is the  recipe:\n\n{ingredient}"}
            ]
        )
        end = time.time()
        logger.error(f"OpenAI took {end - start} seconds")

        nutrtition_info = ai_response.choices[0].message.content
        logger.error(nutrtition_info)
        return nutrtition_info
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        nutrtition_info = None
    return nutrtition_info
