import os, json, urllib.parse, re, tldextract
from google import genai
from google.genai import types
from logging_config import log as logger
from paths import ENV_FILE
from dotenv import load_dotenv
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
        Please analyze these URLs and return the ones likely to contain delivery or return policy information.
        Consider URLs containing keywords like 'shipping', 'delivery', 'returns', 'refunds', 'exchange', 'faq', 'help', 'policy', etc.
        Preserve pages that could potentially contain policy information, but remove most product pages, category pages, and other non-policy pages, but preserve 1 product page as a reference.
        Avoid URLs for privacy policies, terms of service, or other unrelated pages.
        If a URL is ambiguous, include it in the output.

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

def normalize_url(url_string):
    """
    Normalizes a URL for caching purposes.
    - Removes common subdomains (www, www2, m)
    - Converts to https
    - Removes trailing slashes
    - Removes fragments
    - Removes query parameters
    - Lowercases the domain
    """
    try:
        # Add scheme if missing
        if not url_string.startswith(('http://', 'https://')):
            url_string = 'https://' + url_string

        # Parse the URL
        parsed_url = urllib.parse.urlparse(url_string)

        # Extract domain parts
        extracted = tldextract.extract(parsed_url.netloc)

        # Remove common subdomains (www, www2, m)
        if re.match(r'^(www\d*|m)$', extracted.subdomain):
            netloc = f"{extracted.domain}.{extracted.suffix}"
        else:
            netloc = parsed_url.netloc.lower()

        # Reconstruct URL with:
        # - https scheme
        # - no trailing slash
        # - no fragments
        # - no query parameters
        normalized = urllib.parse.urlunparse((
            'https',                              # scheme
            netloc,                               # netloc
            parsed_url.path.rstrip('/'),          # path
            '',                                   # params
            '',                                   # query
            ''                                    # fragment
        ))

        return normalized.lower()

    except Exception as e:
        print(f"Error normalizing URL {url_string}: {e}")
        return url_string
