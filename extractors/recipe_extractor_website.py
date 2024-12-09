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
    Function to get website content using ScrapeNinja API.
    """
    api_url = 'https://scrapeninja.p.rapidapi.com/scrape'

    querystring = {'url': url}

    headers = {
        'x-rapidapi-key': '1776083f1dmsh864701c7fc5a69dp1d97f3jsn8cb7620cf8c2',
        'x-rapidapi-host': 'scrapeninja.p.rapidapi.com'
    }

    api_response = requests.get(api_url, headers=headers, params=querystring)
    api_response.raise_for_status()  # Raise an exception for HTTP errors

    data = api_response.json()
    body = data.get('body', '')

    # Create a mock response object with a .text attribute containing body
    class MockResponse:
        def __init__(self, text):
            self.text = text

    return MockResponse(body)


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
    # Make a request to the given URL using ScrapeNinja API
    response = get_website_content(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract title and body content from HTML
    title = soup.title.string if soup.title else 'No title found'

    # Extract all text content from various relevant tags
    body_content = ' '.join(
        element.get_text(separator=' ', strip=True)
        for element in soup.find_all(['p', 'div', 'span', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'])
    )

    print(body_content)

    # Tokenize the body content and print token count
    token_count, tokens = tokenize_text(body_content)
    print(f"Token Count: {token_count}")

    # Check if token count is below 1000
    # if token_count < 1000:
    #     raise ValueError('The content has fewer than 1,000 tokens, which does not meet the minimum requirement.')

    # Limit body content to the first 150,000 characters if it exceeds this character count
    if len(body_content) > 50000:
        body_content = body_content[:50000]  # Truncate to the first 150,000 characters
        print('Character count exceeded 150,000. Truncated content to the first 150,000 characters.')

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
                        "You get information from recipe websites: recipe title, servings with unit if and only if it available, total time, ingredients, "
                        "directions. "
                        "You will output in simple json. You will not output any description of the recipe. "
                        "If there is no content to review, do not make up a recipe, instead output this: 'Cannot identify Recipe. Please try again with another link.'"
                        "You will ALWAYS supply ingredient amounts. You will supply EXACTLY what you find in the text."
                        )
                },
                {"role": "user", "content": f"Title: {title}\nContent: {body_content}\n\n"
                                            f"Never output a '''markdown identifier before you begin, just the pure "
                                            f"formatting."}
            ]
        )
        end = time.time()
        logger.error(f"OpenAI took {end - start} seconds")

        recipe_info = ai_response.choices[0].message.content
        logger.error(recipe_info)
        s3_file_name = f'{uuid.uuid4()}_image.jpg'
        s3_url = save_image_to_s3_from_url(main_image_url, s3_file_name)
        logger.info(f"s3_image: {s3_url}")
        return recipe_info, got_image, s3_url
    except Exception as e:
        logger.error(f"An error occurred while processing the recipe analysis failed: {e}")
    return None, False, None


def analyse_nutrition_base_ingredient(ingredient):
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
