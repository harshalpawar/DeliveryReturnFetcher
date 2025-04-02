"""
Module for scraping web pages using Jina Reader.
"""
import os, json, requests, time
from dotenv import load_dotenv
from paths import ENV_FILE, FETCHED_URLS_JSON
from config import JINA_READER_HEADERS
from logging_config import log as logger
from tqdm import tqdm
from src.utils import normalize_url
load_dotenv(ENV_FILE)

def load_cache():
    """Load the cached responses from fetched_urls.json"""
    try:
        with open(FETCHED_URLS_JSON, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create the file if it doesn't exist
        with open(FETCHED_URLS_JSON, "w") as f:
            json.dump({}, f)
        return {}

def save_cache(cache):
    """Save the cached responses to fetched_urls.json"""
    with open(FETCHED_URLS_JSON, "w") as f:
        json.dump(cache, f, indent=4)

# input: urls
# output: combined_content
# description: scrape content from a list of URLs using Jina Reader API
def jina_reader(urls):
    if not urls:
        logger.error("No URLs provided to scrape.")
        raise ValueError("No URLs provided to scrape.")
    
    JINA_API_KEY = os.getenv("JINA_API_KEY")
    headers = JINA_READER_HEADERS(JINA_API_KEY)
    all_content = []
    
    # Load cached responses
    cache = load_cache()
    
    # Create mapping of original to normalized URLs
    url_mapping = {url: normalize_url(url) for url in urls}
    
    # Determine which URLs need to be fetched (based on normalized versions)
    urls_to_fetch = [url for url in urls if url_mapping[url] not in cache]
    cached_urls = [url for url in urls if url_mapping[url] in cache]
    
    # Process each uncached URL
    if urls_to_fetch:
        logger.info(f"Fetching {len(urls_to_fetch)} new URLs")
        for url in tqdm(urls_to_fetch, desc="Scraping URLs", unit="url"):
            try:
                response = requests.get(f"https://r.jina.ai/{url}", headers=headers)
                response.raise_for_status()
                
                # Cache the successful response using normalized URL as key
                cache[url_mapping[url]] = response.text
                save_cache(cache)
                
                all_content.append(f"URL: {url}\n\nContent:\n{response.text}\n\n")
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                all_content.append(f"URL: {url}\n\nError: {str(e)}\n\n")
            time.sleep(5)
    
    # Add cached responses to content (using original URLs in output)
    if cached_urls:
        logger.info(f"Using {len(cached_urls)} cached responses")
        for url in cached_urls:
            all_content.append(f"URL: {url}\n\nContent:\n{cache[url_mapping[url]]}\n\n")
    
    combined_content = "".join(all_content)
    return combined_content


