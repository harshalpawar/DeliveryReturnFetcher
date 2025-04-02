from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Set
from logging_config import log as logger
from playwright.sync_api import sync_playwright

# Define the keywords to search for (lowercase)
POLICY_KEYWORDS: Set[str] = {
    "shipping",
    "delivery",
    "return",
    "returns",
    "refund",
    "refunds",
    "exchange",
    "exchanges",
    "faq",
    "faqs",
    "policy",
    "help"
}

EXCLUDE_KEYWORDS: Set[str] = {
    "privacy",
    "terms",
    "conditions"
}

def is_valid_policy_link(href, link_text):
    has_policy_keyword = any(keyword in href.lower() or keyword in link_text.lower() for keyword in POLICY_KEYWORDS)
    has_exclude_keyword = any(keyword in href.lower() or keyword in link_text.lower() for keyword in EXCLUDE_KEYWORDS)
    return has_policy_keyword and not has_exclude_keyword

def fetchPolicyPages(brandHomePageURL: str, timeout: int = 20) -> List[str]:
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
    if not brandHomePageURL.startswith(('http://', 'https://')):
        brandHomePageURL = 'https://' + brandHomePageURL
        
    found_urls: Set[str] = set()
    logger.info(f"Attempting to fetch policy pages for: {brandHomePageURL}")

    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # Set timeout
            page.set_default_timeout(timeout * 1000)  # Convert to milliseconds
            
            # Navigate to the page
            logger.info(f"Navigating to {brandHomePageURL}...")
            page.goto(brandHomePageURL, wait_until='networkidle')
            
            # Get the fully rendered HTML content
            html_content = page.content()
            
            # Close browser
            browser.close()
            logger.info("Browser closed.")

    except Exception as e:
        logger.error(f"Error occurred while fetching {brandHomePageURL}: {e}")
        return []

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)  # Find all anchor tags with an href attribute

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
    return sorted(list(found_urls))  # Return sorted list for consistency

# --- Example Usage ---
if __name__ == "__main__":
    homepage_url = "https://volcape.com/"

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
