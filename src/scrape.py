"""
Module for scraping web pages using Jina Reader.
"""
import os, json, requests, time
from dotenv import load_dotenv
from paths import ENV_FILE
from config import JINA_READER_HEADERS
from logging_config import log as logger
from tqdm import tqdm

load_dotenv(ENV_FILE)
# input: urls
# output: combined_content
# description: scrape content from a list of URLs using Jina Reader API
def jina_reader(urls):
    
    if not urls:
        logger.error("No URLs provided to scrape.")
        raise ValueError("No URLs provided to scrape.")
    
    JINA_API_KEY = os.getenv("JINA_API_KEY")
    headers = JINA_READER_HEADERS(JINA_API_KEY)
    
    # List to store all scraped content
    all_content = []
    
    # Process each URL
    # TODO: add a progress bar
    # TODO: add a retry mechanism
    # TODO: add a timeout mechanism
    # TODO: add request rotation
    # TODO: add parallel requests
    for url in tqdm(urls, desc="Scraping URLs", unit="url"):
        try:
            response = requests.get(f"https://r.jina.ai/{url}", headers=headers)
            logger.info(f"Response: {response.text}")
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            continue
        
        try:
            all_content.append(f"URL: {url}\n\nContent:\n{response.text}\n\n") 
        except (KeyError, json.JSONDecodeError) as e:
            all_content.append(f"URL: {url}\n\nError extracting content: {str(e)}\n\n")
            logger.error(f"Error extracting content: {str(e)}") 
        except Exception as e:
            all_content.append(f"URL: {url}\n\nUnexpected error: {str(e)}\n\n")
            logger.error(f"Unexpected error: {str(e)}")
        time.sleep(5)
    
    combined_content = "".join(all_content)
    return combined_content


