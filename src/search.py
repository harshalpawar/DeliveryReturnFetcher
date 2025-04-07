"""
Module for handling Jina AI search operations to find relevant policy pages.
"""
import os, requests, json
from dotenv import load_dotenv
from paths import ENV_FILE, SEARCH_CACHE
from config import SEARCH_KEYWORDS, JINA_SEARCH_HEADERS
from logging_config import log as logger
from src.policy_page_fetcher import fetchPolicyPages
from src.utils import deduplicate_urls, gemini_url_filter, remove_url_tag
load_dotenv(ENV_FILE)

# input: brand_name, brand_domain
# output: list of URLs to policy pages
# description: search for policy-related pages on a brand's website using Jina AI
def jina_search(brand_name, brand_domain):
    # check cache
    try:
        with open(SEARCH_CACHE, 'r') as cache_file:
            cache_data = json.load(cache_file)
    except (FileNotFoundError, json.JSONDecodeError):
        cache_data = {}

    if brand_name in cache_data:
        logger.info(f"Found cached search results for {brand_name} in {SEARCH_CACHE}")
        return cache_data[brand_name]

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
        policy_pages = fetchPolicyPages(brand_domain)
        # Combine and deduplicate URLs using normalization
        all_urls = deduplicate_urls(policy_pages + urls_delivery + urls_return)

        logger.info(f"Found {len(all_urls)} unique URLs for {brand_name}")

        # Filter URLs using Gemini
        filtered_urls = gemini_url_filter(all_urls, brand_name)
        logger.info(f"After Gemini filtering: {len(filtered_urls)} URLs remaining")

        cache_search(brand_name, filtered_urls)
        return filtered_urls

    except Exception as e:
        logger.error(f"Unexpected error in jina_search: {e}")
        raise e

def cache_search(brand_name, urls):
    # Cache the search results
    try:
        with open(SEARCH_CACHE, 'r') as cache_file:
            cache_data = json.load(cache_file)
    except (FileNotFoundError, json.JSONDecodeError):
        cache_data = {}

    # Store the results in the cache
    cache_data[brand_name] = urls

    # Write the updated cache back to the file
    with open(SEARCH_CACHE, 'w') as cache_file:
        json.dump(cache_data, cache_file, indent=2)

    logger.info(f"Cached search results for {brand_name} in {SEARCH_CACHE}")

