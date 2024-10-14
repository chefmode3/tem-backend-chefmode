import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from PIL import Image
from io import BytesIO
import re
import os
import random
import time
import tiktoken  # Import tiktoken

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_main_image(soup):
    """
    Attempt to extract the main image from a given soup object.
    """
    image = soup.find('meta', property='og:image')
    if image and 'content' in image.attrs:
        return image['content']
    # Fallback for cases where there is no og:image
    image_tags = soup.find_all('img', src=True)
    if image_tags:
        return image_tags[0]['src']
    return None

def get_website_content(url):
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

def main():
    st.title("Recipe Scraper and Analyzer")

    # Input link from user
    url = st.text_input("Paste a link to a recipe website")

    if url:
        try:
            # Make a request to the given URL with retries and user-agent spoofing
            response = get_website_content(url)

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title and body content from HTML
            title = soup.title.string if soup.title else "No title found"
            # Extract all text content from various relevant tags
            body_content = " ".join(
                element.get_text(separator=" ", strip=True)
                for element in soup.find_all(['p', 'div', 'span', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'])
            )

            print(body_content)

            # Tokenize the body content and print token count
            token_count, tokens = tokenize_text(body_content)
            st.write(f"Token Count: {token_count}")

            # Extract main image
            main_image_url = extract_main_image(soup)

            # Display the main image if found
            if main_image_url:
                if not re.match(r'^https?:', main_image_url):
                    main_image_url = requests.compat.urljoin(url, main_image_url)
                image = get_image_with_retry(main_image_url)
                if image:
                    st.image(image, caption="Recipe Image")
                else:
                    st.write("Failed to retrieve the main image after multiple attempts.")
            else:
                st.write("No main image found.")

            # Use OpenAI to analyze the recipe content
            ai_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You get information from recipe websites: recipe title, ingredients, directions. You will output in simple markdown. You will not output any description of the recipe. You will ALWAYS supply ingredient amounts. You will supply EXACTLY what you find in the text."},
                    {"role": "user", "content": f"Title: {title}\nContent: {body_content}"}
                ]
            )

            recipe_info = ai_response.choices[0].message.content

            # Display the AI response
            st.markdown(recipe_info)

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to retrieve the website: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
