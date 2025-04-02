"""
Module for handling Jina AI search operations to find relevant policy pages.
"""
import os, requests
from dotenv import load_dotenv
from paths import ENV_FILE
from config import SEARCH_KEYWORDS, JINA_SEARCH_HEADERS
from logging_config import log as logger
from src.utils import normalize_url
from src.policy_page_fetcher import fetchPolicyPages
load_dotenv(ENV_FILE)


def remove_url_tag(content: str) -> str:
    """
    Remove the srsltid parameter from a URL.
    
    Args:
        content (str): The full URL potentially containing the srsltid tag
    
    Returns:
        str: The cleaned URL without the srsltid parameter
    """
    # Split the URL at '?' to separate base URL from parameters
    parts = content.split('?')
    
    # If there are parameters, filter out the srsltid
    if len(parts) > 1:
        # Keep only parameters that don't start with 'srsltid'
        clean_params = [param for param in parts[1].split('&') if not param.startswith('srsltid=')]
        
        # Reconstruct the URL
        if clean_params:
            return f"{parts[0]}?{'&'.join(clean_params)}"
        else:
            return parts[0]
    
    return content


def deduplicate_urls(urls):
    """
    Deduplicate URLs based on their normalized form while preserving original URLs.
    Returns one original URL for each unique normalized form.
    """
    normalized_map = {}  # normalized_url -> original_url
    for url in urls:
        norm_url = normalize_url(url)
        if norm_url not in normalized_map:
            normalized_map[norm_url] = url
    
    return list(normalized_map.values())


# input: brand_name, brand_domain
# output: list of URLs to policy pages
# description: search for policy-related pages on a brand's website using Jina AI
def jina_search(brand_name, brand_domain):
    # TODO: add a fallback mechanism
    JINA_API_KEY = os.getenv("JINA_API_KEY")
    
    url_delivery = f"https://s.jina.ai/?q={SEARCH_KEYWORDS['delivery']}&gl=IN&location=Mumbai&hl=en"
    url_return = f"https://s.jina.ai/?q={SEARCH_KEYWORDS['returns']}&gl=IN&location=Mumbai&hl=en"
    headers = JINA_SEARCH_HEADERS(JINA_API_KEY, brand_domain)
    
    try:
        response_delivery = requests.get(url_delivery, headers=headers)
        response_delivery.raise_for_status()
        response_return = requests.get(url_return, headers=headers)
        response_return.raise_for_status()

        response_data_delivery = response_delivery.json()
        response_data_return = response_return.json()

        if response_data_delivery.get("data", []) == None:
            raise Exception(f"No delivery policy found for {brand_name}")
        if response_data_return.get("data", []) == None:
            raise Exception(f"No return policy found for {brand_name}")
        
        # Extract URLs from both responses
        urls_delivery = [remove_url_tag(item["url"]) for item in response_data_delivery["data"]]
        urls_return = [remove_url_tag(item["url"]) for item in response_data_return["data"]]
        
        # Combine and deduplicate URLs using normalization
        all_urls = deduplicate_urls(urls_delivery + urls_return + fetchPolicyPages(brand_domain))
        
        logger.info(f"Found {len(all_urls)} unique URLs for {brand_name}")
        return all_urls
        
    except Exception as e:
        logger.error(f"Unexpected error in jina_search: {e}")
        raise e

