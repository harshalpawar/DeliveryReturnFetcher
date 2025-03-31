import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Set
from logging_config import log as logger

# Define the keywords to search for (lowercase)
POLICY_KEYWORDS: Set[str] = {
    "shipping",
    "delivery",
    "return",
    "returns",
    "refund",
    "refunds",
    "exchange",
    "faq",
    "faqs",
    "policy",
    "help"
}
EXCLUDE_KEYWORDS: Set[str] = {
    "privacy",
    "terms",
    "condition"
}
def is_valid_policy_link(href, link_text):
    has_policy_keyword = any(keyword in href.lower() or keyword in link_text.lower() for keyword in POLICY_KEYWORDS)
    has_exclude_keyword = any(keyword in href.lower() or keyword in link_text.lower() for keyword in EXCLUDE_KEYWORDS)
    return has_policy_keyword and not has_exclude_keyword

# Define a common browser user agent to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetchPolicyPages(brandHomePageURL: str, timeout: int = 10) -> List[str]:
    """
    Scrapes a given homepage URL to find and return links potentially
    leading to policy pages (shipping, delivery, returns, etc.).

    Args:
        brandHomePageURL: The URL of the brand's homepage.
        timeout: Request timeout in seconds.

    Returns:
        A list of absolute URLs found on the homepage that contain
        policy-related keywords in their href or link text.
        Returns an empty list if an error occurs or no relevant links are found.
    """
    brandHomePageURL = "https://" + brandHomePageURL
    found_urls: Set[str] = set()

    logger.info(f"Attempting to fetch policy pages for: {brandHomePageURL}")
    response = requests.get(brandHomePageURL, headers=HEADERS, timeout=timeout)
    try:
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error occurred: {e}")
        logger.error(f"Status Code: {response.status_code}")
        return []  # Return an empty list to indicate no policy pages found

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True) # Find all anchor tags with an href attribute

    for link_tag in links:
        href = link_tag['href']
        link_text = link_tag.get_text(strip=True).lower()

        # Basic filtering for non-relevant hrefs
        if not href or href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
            continue

        # Check if any keyword exists in the href or link text
        if is_valid_policy_link(href, link_text):

            # Convert relative URLs to absolute URLs
            absolute_url = urljoin(brandHomePageURL, href)

            # Basic validation to ensure it's likely an HTTP/HTTPS URL
            if absolute_url.startswith(('http://', 'https://')):
                found_urls.add(absolute_url)

    logger.info(f"Potential policy page URLs found: {found_urls}")
    return sorted(list(found_urls)) # Return sorted list for consistency

# --- Example Usage ---
if __name__ == "__main__":
    # Example: Replace with an actual brand homepage URL
    homepage_url = "https://volcape.com/"
    # homepage_url = "https://www.myntra.com/" # Another example

    if homepage_url:
        policy_urls = fetchPolicyPages(homepage_url)
        if policy_urls:
            print("\nPotential Policy Page URLs Found:")
            for url in policy_urls:
                print(url)
        else:
            print("\nNo potential policy page URLs found or an error occurred.")
    else:
        print("Please provide a homepage URL in the example usage section.")
