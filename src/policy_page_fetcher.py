from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Set, Optional, Tuple
from logging_config import log as logger
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import requests

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

def fetch_with_requests(url: str, timeout: int = 20) -> str:
    """
    Attempt to fetch page content using requests library.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds

    Returns:
        str: HTML content if successful, empty string if failed
    """
    logger.info(f"Requests: Attempting to fetch policy pages for: {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }

        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        logger.info(f"Requests: Successfully fetched {url}")
        return response.text
    except Exception as e:
        logger.error(f"Requests fallback failed for {url}: {e}")
        return ""

def is_valid_policy_link(href, link_text):
    has_policy_keyword = any(keyword in href.lower() or keyword in link_text.lower() for keyword in POLICY_KEYWORDS)
    has_exclude_keyword = any(keyword in href.lower() or keyword in link_text.lower() for keyword in EXCLUDE_KEYWORDS)
    return has_policy_keyword and not has_exclude_keyword

def fetch_with_playwright(url: str, timeout: int = 20, user_agent: Optional[str] = None) -> str:
    """
    Attempt to fetch page content using Playwright.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        user_agent: Optional custom user agent string

    Returns:
        str: HTML content if successful, empty string if failed
    """
    logger.info(f"Playwright: Attempting to fetch policy pages for: {url}")

    try:
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)

            # Set up default or custom user agent
            if not user_agent:
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

            # Create context with user agent and viewport
            context = browser.new_context(
                user_agent=user_agent,
                viewport={'width': 1280, 'height': 720}
            )
            page = context.new_page()

            # Apply stealth mode
            stealth_sync(page)

            # Set timeout
            page.set_default_timeout(timeout * 1000)  # Convert to milliseconds

            # Navigate to the page with fallback
            try:
                page.goto(url, wait_until='networkidle', timeout=timeout * 1000)
            except Exception as e:
                logger.warning(f"Networkidle timeout, retrying with load event: {e}")
                page.goto(url, wait_until='load', timeout=timeout * 1000)

            # Wait for any dynamic content
            page.wait_for_timeout(2000)  # 2 second grace period

            # Get the fully rendered HTML content
            html_content = page.content()
            logger.info(f"Playwright: Successfully fetched {url}")
            # Close browser
            browser.close()
            return html_content

    except Exception as e:
        logger.error(f"Playwright failed while fetching {url}: {e}")
        return ""

def markdownify(html_content: str, base_url: str) -> List[str]:
    """
    Process HTML content to extract policy-related URLs.

    Args:
        html_content: The HTML content to process
        base_url: The base URL for resolving relative URLs

    Returns:
        List[str]: List of found policy-related URLs
    """
    found_urls: Set[str] = set()

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
            absolute_url = urljoin(base_url, href)

            # Basic validation to ensure it's likely an HTTP/HTTPS URL
            if absolute_url.startswith(('http://', 'https://')):
                found_urls.add(absolute_url)

    logger.info(f"Found {len(found_urls)} potential policy page URLs")
    if found_urls:
        logger.debug(f"URLs found: {found_urls}")
    return sorted(list(found_urls))  # Return sorted list for consistency

def fetchPolicyPages(brandHomePageURL: str, timeout: int = 20, user_agent: str = None) -> List[str]:
    """
    Scrapes a given homepage URL to find and return links potentially
    leading to policy pages (shipping, delivery, returns, etc.).

    Args:
        brandHomePageURL: The URL of the brand's homepage.
        timeout: Request timeout in seconds.
        user_agent: Optional custom user agent string.

    Returns:
        A list of absolute URLs found on the homepage that contain
        policy-related keywords in their href or link text.
        Returns an empty list if an error occurs or no relevant links are found.
    """
    if not brandHomePageURL.startswith(('http://', 'https://')):
        brandHomePageURL = 'https://' + brandHomePageURL

    # Try with Playwright first
    html_content = fetch_with_playwright(brandHomePageURL, timeout, user_agent)

    # If Playwright fails, try with requests
    if not html_content:
        html_content = fetch_with_requests(brandHomePageURL, timeout)

    # If both methods failed, return empty list
    if not html_content:
        logger.error("Both Playwright and requests failed to fetch the page")
        return []

    # Process the HTML content and return the found URLs
    return markdownify(html_content, brandHomePageURL)

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
