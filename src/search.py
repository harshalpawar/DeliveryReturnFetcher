"""
Module for handling Jina AI search operations to find relevant policy pages.
"""
import os, requests
from dotenv import load_dotenv
from paths import ENV_FILE
from config import SEARCH_KEYWORDS, JINA_SEARCH_HEADERS
from logging_config import log as logger
load_dotenv(ENV_FILE)

# input: brand_name, brand_domain
# output: list of URLs to policy pages
# description: search for policy-related pages on a brand's website using Jina AI
def jina_search(brand_name, brand_domain):
    JINA_API_KEY = os.getenv("JINA_API_KEY")
    
    # Prepare search URLs for delivery and return policies
    url_delivery = f"https://s.jina.ai/?q={SEARCH_KEYWORDS['delivery']}&gl=IN&location=Mumbai&hl=en"
    url_return = f"https://s.jina.ai/?q={SEARCH_KEYWORDS['returns']}&gl=IN&location=Mumbai&hl=en"
    
    # Prepare headers
    headers = JINA_SEARCH_HEADERS(JINA_API_KEY, brand_domain)
    
    try:
        # Make requests
        response_delivery = requests.get(url_delivery, headers=headers)
        response_return = requests.get(url_return, headers=headers)
        
        # Parse JSON responses
        response_data_delivery = response_delivery.json()
        response_data_return = response_return.json()
        logger.info(f"Delivery response: {response_data_delivery}")
        logger.info(f"Return response: {response_data_return}")
        if response_data_delivery.get("data", []) == None:
            raise Exception(f"No delivery policy found for {brand_name}")
        if response_data_return.get("data", []) == None:
            raise Exception(f"No return policy found for {brand_name}")
        
        # Extract URLs from both responses and combine them
        urls_delivery = [item["url"] for item in response_data_delivery["data"]]
        urls_return = [item["url"] for item in response_data_return["data"]]
        all_urls = list(set(urls_delivery + urls_return))
        
        logger.info(f"Found {len(all_urls)} unique URLs for {brand_name}")
        return all_urls
        
    except Exception as e:
        logger.error(f"Unexpected error in jina_search: {e}")
        raise e



