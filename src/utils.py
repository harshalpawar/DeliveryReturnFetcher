import urllib.parse
import tldextract
import re

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