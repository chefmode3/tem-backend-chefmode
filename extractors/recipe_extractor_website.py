from __future__ import annotations

import json
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


def get_website_content_v2(url):
    """
        Function to get website content using ScrapeNinja API.
        """
    api_url = 'https://scrapeninja.p.rapidapi.com/scrape'

    try:
        querystring = {'url': url}

        headers = {
            'x-rapidapi-key': '1776083f1dmsh864701c7fc5a69dp1d97f3jsn8cb7620cf8c2',
            'x-rapidapi-host': 'scrapeninja.p.rapidapi.com'
        }

        api_response = requests.get(api_url, headers=headers, params=querystring)
        api_response.raise_for_status()  # Raise an exception for HTTP errors

        # data = api_response.json()

        return api_response
    except Exception:
        return None


def get_website_content(url, retry_count: int = 0, proxies=None):
    """
    Function to handle website requests with retries for handling 403 errors.
    """
    headers_list = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        },
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        },
        {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        },
    ]

    MAX_RETRIES = 5
    # for _ in range(5):  # Retry up to 5 times
    status_code = None
    try:
        headers = random.choice(headers_list)
        response = requests.get(url, headers=headers, proxies=proxies)
        print(response.text)
        response.raise_for_status()
        status_code = response.status_code
        return response
    except Exception as e:
        logger.error(e)
        logger.error(f"status code {status_code}")
        if retry_count < MAX_RETRIES + 1:
            retry_count += 1
            print(f"Download failed. Retrying ({retry_count}/{MAX_RETRIES - 1})...")
            host = os.getenv("YOUTUBE_PROXY_HOST")
            port = os.getenv("YOUTUBE_PROXY_PORT")

            username = os.getenv("YOUTUBE_PROXY_USERNAME")
            password = os.getenv("YOUTUBE_PROXY_PASSWORD")

            proxies = {
                'https': f'http://ashishbishnoi18:DW2GTLWb8gzyOQDj@proxy.packetstream.io:31112',
            }

            if status_code == 403:
                time.sleep(random.uniform(1, 3))  # Random sleep to avoid being blocked
                return get_website_content(url, proxies=proxies, retry_count=retry_count)
            time.sleep(random.uniform(1, 15))

            return get_website_content(url, proxies=proxies, retry_count=retry_count)
        else:
            return get_website_content_v2(url)  # get_website_content_v2(url)


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
    # Make a request to the given URL with retries and user-agent spoofing
    start = time.time()

    response = get_website_content(url)
    if not response:
        return {'error': 'Failed to fetch website content. Please try again.'}, False, None
    end = time.time()
    print(f"get_website_content took {end - start} seconds")

    # Parse the HTML content
    start = time.time()
    soup = BeautifulSoup(response.text, 'html.parser')
    end = time.time()
    print(f"parsing html took {end - start} seconds")

    # Extract title and body content from HTML
    title = soup.title.string if soup.title else "No title found"

    start = time.time()
    # Extract all text content from various relevant tags

    body_content = soup.body.get_text(separator=" ", strip=True)
    end = time.time()
    # print(f"Extract all
    # # Extract all text content from various relevant tags
    body_content = " ".join(
        element.get_text(separator=" ", strip=True)
        for element in soup.find_all(['p', 'div', 'span', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'])
    )

    print(f"body text scrap: {body_content}")
    print(f"len of body {len(body_content)}")

    token_count, tokens = tokenize_text(body_content)
    print(f"Token Count: {token_count}")

    # Check if token count is below 1000
    if token_count < 1000:
        raise ValueError("The content has fewer than 1,000 tokens, which does not meet the minimum requirement.")

    # Limit body content to the first 150,000 characters if it exceeds this character count
    if len(body_content) > 150000:
        body_content = body_content[:150000]  # Truncate to the first 150,000 characters
        print('Character count exceeded 150,000. Truncated content to the first 150,000 characters.')

    # Extract main image
    main_image_url = extract_main_image(soup)
    got_image = bool(main_image_url)

    # Analyze content using AI
    try:
        analyse_recipe_message = [
            {
                "role": "system",
                "content": (
                    "You get information from recipe websites: recipe title, servings, total time, ingredients, directions. "
                    "You will output in simple markdown. You will not output any description of the recipe. "
                    "If there is no content to review, do not make up a recipe, instead output this: 'Cannot identify Recipe. Please try again with another link.'"
                    "You will ALWAYS supply ingredient amounts. You will supply EXACTLY what you find in the text. "
                    "YOU MUST AND WILL ALWAYS GIVE THE FULL RECIPES, AND MUST BE IN ORDER. "
                    "IMPORTANT: The recipe **MUST NOT BE TRUNCATED**. Include every section: title, servings, total time, ingredients, and directions. Complete information is mandatory."

                )
            },
            {
                "role": "user",
                "content": f"Title: {title}\nContent: {body_content}\n\n"
                           f"Never output a '''markdown identifier before you begin, just the pure formatting. "
                           "IMPORTANT: The recipe **MUST NOT BE TRUNCATED**. Include every section: title, servings, total time, ingredients, and directions. Complete information is mandatory."

            }
        ]
        recipe_info_markdown = get_complete_response(messages=analyse_recipe_message)

        logger.error(recipe_info_markdown)
        recipe_info = group_markdown_to_json(recipe_info_markdown)
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
        nutrition_base_ingredient_message = [
            {
                "role": "system",
                "content": (
                    "You are a nutrition calculation assistant. "
                    "Your task is to analyze recipes and provide accurate nutritional information. "
                    "Ensure ingredient names NEVER appear as nutrients. "
                    "Instead, use categories like 'calories', 'protein', 'fats', 'carbohydrates', and micronutrients such as 'vitamin C', 'fiber', etc. "
                    "Your response MUST strictly follow this JSON format: "
                    "{ 'nutritions': [ "
                    "    { 'name': 'string', 'quantity': float, 'unit': 'string' } "
                    "]}. "
                    "If specific nutrients cannot be determined, set quantity as 0."
                )
            },
            {"role": "user", "content": f"Here is the recipe:\n\n{ingredient}"}
        ]
        nutrtition_info = get_complete_response(messages=nutrition_base_ingredient_message)
        # logger.error(nutrtition_info)
        return nutrtition_info
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        nutrtition_info = None
    return nutrtition_info


def group_markdown_to_json(recipe_info_markdown):
    try:
        group_markdown_to_json_messages = [
            {
                'role': 'system',
                'content': (
                    "You get information from recipe websites: recipe, title, servings with unit if and only if it available, total time, ingredients, "
                    "directions. "
                    "For each recipe described in the text, retrieve ONLY the "
                    "following fields:"
                    "title: (The recipe's name),"
                    "servings: (Number of servings, if stated),"

                    "total_time: (Total preparation and cooking time as a single string),"
                    "ingredients: (Each ingredient should a single line for it),"
                    "directions: (A list of steps for making the recipe, numbered or as separate entries, exactly as described in the order they appear in the video)."
                    "if title of ingredient  or title direction is not available, use 'None' as the title value"
                    "No nested objects other than these ones."
                    "Never output a '''markdown identifier before you begin and return the value in object format that can easily convert into the json"
                    "You will output in simple json. You will not output any description of the recipe. "
                    "If there is no content to review, do not make up a recipe, instead output this: 'Cannot identify Recipe. Please try again with another link.'"
                    "You will ALWAYS supply ingredient amounts. You will supply EXACTLY what you find in the text."

                    "'title': 'string',"
                    " 'servings': 'string',"
                    " 'preparation_time': 'string',"

                    "'ingredients': ["
                    " {"
                    "     'title_of_ingredient': 'string',"
                    "    'list': ["
                    "     'string'"
                    "  ]"
                    "   }"
                    " ],"
                    " 'directions': ["
                    "  {"
                    "     'title_of_direction': 'string',"
                    "    'list': ["
                    "     'string'"
                    "  ]"
                    "   },"

                    "  ]"
                    "IMPORTANT: The recipe **MUST NOT BE TRUNCATED**. Include every section: title, servings, total time, ingredients, and directions. Complete information is mandatory."

                )
            },
            {'role': 'user', 'content': f"Here is the  markdown text:\n\n{recipe_info_markdown}"}
        ]
        json_info = get_complete_response(messages=group_markdown_to_json_messages)

        logger.error(json_info)
        return json_info
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        json_info = None
    return json_info


def get_complete_response(messages):
    complete_response = ""
    max_retries = 3
    attempts = 0

    while attempts < max_retries:
        start = time.time()
        ai_response = client.chat.completions.create(
            model='gpt-4-turbo',
            messages=messages,
        )
        end = time.time()
        logger.error(f"OpenAI took {end - start} seconds")
        break_out = False
        # Extract content and finish reason from response
        # choice = ai_response.choices[0]
        for choice in ai_response.choices:
            current_response = choice.message.content
            finish_reason_1 = choice.finish_reason
            logger.error(f"Finish reason: {finish_reason_1}")

            complete_response += current_response.strip() + "\n"

            # Break if generation is complete
            if finish_reason_1 == "stop":
                break_out = True
                logger.error(f"Finish reason: {current_response}")
                logger.info("bread out ")
                break
            if finish_reason_1 == "content_filter":
                break_out = True
                logger.info("bread out content_filter")
                break

        if break_out:
            break

        # logger.warning("Truncated response detected, requesting continuation...")
        # # messages.append({"role": "assistant", "content": current_response})
        # messages.append({"role": "user", "content": "IMPORTANT: The recipe **MUST NOT BE TRUNCATED**.."})

        attempts += 1

    if attempts == max_retries:
        logger.error("Maximum continuation attempts reached. Recipe may be incomplete.")

    return complete_response.strip()

