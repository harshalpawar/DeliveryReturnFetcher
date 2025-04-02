"""
Module for scraping web pages using Jina Reader and Playwright as fallback.
"""
import os, json, requests, time
from dotenv import load_dotenv
from paths import ENV_FILE, FETCHED_URLS_JSON
from config import JINA_READER_HEADERS
from logging_config import log as logger
from tqdm import tqdm
from src.utils import normalize_url
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from markdownify import markdownify as md
load_dotenv(ENV_FILE)

# List of brands that should use Playwright directly instead of Jina
USE_PLAYWRIGHT = [
    "Fabindia"
]

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
def jina_reader(urls, brand_name=None):
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
            max_retries = 2
            retry_count = 0
            success = False
            
            # Check if we should use Playwright directly for this brand
            if brand_name and brand_name in USE_PLAYWRIGHT:
                logger.info(f"Using Playwright directly for {brand_name}")
                playwright_content = scrape_with_playwright(url)
                if not playwright_content.startswith("Error"):
                    cache[url_mapping[url]] = playwright_content
                    save_cache(cache)
                    all_content.append(f"URL: {url}\n\nContent:\n{playwright_content}\n\n")
                else:
                    logger.error(f"Playwright failed for {url}")
                    all_content.append(f"URL: {url}\n\nError: Failed with Playwright\n\n")
            else:
                # Use Jina with Playwright fallback
                while retry_count < max_retries and not success:
                    try:
                        # Try Jina Reader first
                        response = requests.get(
                            f"https://r.jina.ai/{url}", 
                            headers=headers
                        )
                        response.raise_for_status()
                        
                        # Cache the successful response using normalized URL as key
                        cache[url_mapping[url]] = response.text
                        save_cache(cache)
                        
                        all_content.append(f"URL: {url}\n\nContent:\n{response.text}\n\n")
                        success = True
                        
                    except Exception as e:
                        retry_count += 1
                        if retry_count < max_retries:
                            logger.warning(f"Jina Reader attempt {retry_count} failed for {url}: {e}. Retrying...")
                            time.sleep(5)
                        else:
                            logger.warning(f"Jina Reader failed for {url}: {e}. Trying Playwright fallback...")
                            # Try Playwright as fallback
                            playwright_content = scrape_with_playwright(url)
                            if not playwright_content.startswith("Error"):
                                # Cache the successful Playwright response
                                cache[url_mapping[url]] = playwright_content
                                save_cache(cache)
                                all_content.append(f"URL: {url}\n\nContent:\n{playwright_content}\n\n")
                                success = True
                            else:
                                logger.error(f"Both Jina and Playwright failed for {url}")
                                all_content.append(f"URL: {url}\n\nError: Failed with both Jina and Playwright\n\n")
            
            time.sleep(5)  # Rate limiting between requests
    
    # Add cached responses to content (using original URLs in output)
    if cached_urls:
        logger.info(f"Using {len(cached_urls)} cached responses")
        for url in cached_urls:
            all_content.append(f"URL: {url}\n\nContent:\n{cache[url_mapping[url]]}\n\n")
    
    combined_content = "".join(all_content)
    return combined_content

def scrape_with_playwright(url, user_agent=None, headers=None):
    """
    Fetches HTML using Playwright with stealth and custom headers,
    and converts it to Markdown as a fallback mechanism.

    Args:
        url (str): The URL to scrape.
        user_agent (str, optional): User agent string to use. If None, a default will be used.
        headers (dict, optional): Custom headers to send with the request. Defaults to None.

    Returns:
        str: Markdown content of the webpage or an error message.
    """
    try:
        with sync_playwright() as p:
            logger.info(f"Fetching {url} with Playwright")
            browser = p.chromium.launch(headless=True)  # Use headless for production
            
            # Initialize headers if None
            if headers is None:
                headers = {}
            
            # Set up default or custom user agent
            if not user_agent:
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            
            # Combine user agent with other headers
            all_headers = {"User-Agent": user_agent, **headers}
            
            # Create context with headers
            context = browser.new_context(
                user_agent=user_agent,
                viewport={'width': 1280, 'height': 720}
            )
            page = context.new_page()
            
            # Apply stealth
            stealth_sync(page)
            
            # Set additional headers if any
            if headers:
                page.set_extra_http_headers(headers)
            
            try:
                page.goto(url, wait_until='networkidle', timeout=30000)
            except Exception as e:
                page.goto(url, wait_until='load', timeout=30000)
            
            # Wait for any dynamic content
            page.wait_for_timeout(2000)
            
            html_content = page.content()
            
            browser.close()
            logger.info(f"Successfully fetched {url} with Playwright")

        # Convert to Markdown
        markdown_content = md(html_content)
        return markdown_content

    except Exception as e:
        logger.error(f"Error in Playwright scraping for {url}: {e}")
        return f"Error scraping with Playwright: {str(e)}"


