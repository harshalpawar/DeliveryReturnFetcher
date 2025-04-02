"""
Module for handling Jina AI search operations to find relevant policy pages.
"""
import os, requests, json
from dotenv import load_dotenv
from paths import ENV_FILE
from config import SEARCH_KEYWORDS, JINA_SEARCH_HEADERS
from logging_config import log as logger
from src.utils import normalize_url
from src.policy_page_fetcher import fetchPolicyPages
from google import genai
from google.genai import types
load_dotenv(ENV_FILE)



def gemini_url_filter(urls, brand_name):
    """
    Filter URLs using Gemini to identify the most relevant policy pages.
    
    Args:
        urls (list): List of URLs to filter
        brand_name (str): Name of the brand for context
        
    Returns:
        list: Filtered list of URLs deemed relevant for delivery and return policies
    """
    try:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Prepare the prompt
        user_prompt = f"""
        You are a URL filtering expert. I have a list of URLs from {brand_name}'s website that might contain delivery and return policies.
        Please analyze these URLs and return ONLY the ones most likely to contain delivery or return policy information.
        Consider URLs containing keywords like 'shipping', 'delivery', 'returns', 'exchange', 'faq', 'help', 'policy', etc.
        Preserve pages that could potentially contain policy information, but remove most product pages, category pages, and other non-policy pages, but preserve 1 product page as a reference.
        Avoid URLs for privacy policies, terms of service, or other unrelated pages.

        URLs to analyze:
        {json.dumps(urls, indent=2)}

        Example input:
        [
          "https://example.com/shipping-and-delivery",
          "https://example.com/returns-policy",
          "https://example.com/privacy-policy",
          "https://example.com/products/shoes",
          "https://example.com/help/order-tracking",
          "https://example.com/terms-of-service",
          "https://example.com/faq/returns"
        ]

        Example output:
        [
          "https://example.com/shipping-and-delivery",
          "https://example.com/returns-policy",
          "https://example.com/help/order-tracking",
          "https://example.com/faq/returns"
        ]

        Return the filtered URLs as a JSON array with no additional text or explanation.
        """
        
        # Make the API call to Gemini
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-thinking-exp-01-21",
                config=types.GenerateContentConfig(
                    temperature=0.1  # Low temperature for more focused results
                ),
                contents=user_prompt
            )
            
            # Clean and parse the response
            response_text = response.text.strip()
            
            # Extract JSON content from markdown code block
            if '```json' in response_text:
                # Split by ```json and take the content after it
                json_content = response_text.split('```json')[-1]
                # Remove trailing ``` if present
                json_content = json_content.split('```')[0]
            else:
                json_content = response_text
                
            # Clean the extracted content
            json_content = json_content.strip()
            
            try:
                filtered_urls = json.loads(json_content)
                if not isinstance(filtered_urls, list):
                    logger.error("Parsed response is not a list")
                    logger.error(f"Response text was: {response_text}")
                    return urls
                
                # Ensure all returned URLs were in the original list
                filtered_urls = [url for url in filtered_urls if url in urls]
                return filtered_urls
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Response text was: {response_text}")
                return urls
        
        except Exception as e:
            logger.error(f"Error in Gemini API call: {e}")
            return urls
            
    except Exception as e:
        logger.error(f"Error in gemini_url_filter: {e}")
        # Return original URLs if filtering fails
        return urls


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
        policy_pages = fetchPolicyPages(brand_domain)
        # Combine and deduplicate URLs using normalization
        all_urls = deduplicate_urls(policy_pages + urls_delivery + urls_return)
        
        logger.info(f"Found {len(all_urls)} unique URLs for {brand_name}")
        
        # Filter URLs using Gemini
        # filtered_urls = gemini_url_filter(all_urls, brand_name)
        filtered_urls = all_urls
        logger.info(f"After Gemini filtering: {len(filtered_urls)} URLs remaining")
        
        return filtered_urls
        
    except Exception as e:
        logger.error(f"Unexpected error in jina_search: {e}")
        raise e

