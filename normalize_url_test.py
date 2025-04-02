from src.utils import normalize_url

test_urls = [
    # Basic URLs
    "www.example.com",
    "http://www.example.com",
    "https://example.com",
    
    # Subdomains
    "www2.example.com",
    "m.example.com",
    "blog.example.com",  # This subdomain should be preserved
    
    # Paths and slashes
    "example.com/",
    "example.com/path/",
    "example.com/path//",
    
    # Query parameters and fragments
    "example.com/path?param=value",
    "example.com/path#section",
    "example.com/path?param=value#section",
    
    # Mixed cases
    "Example.Com",
    "EXAMPLE.COM/PATH",
    
    # Real-world examples
    "www2.hm.com/en_in",
    "www.zara.com/in",
    "m.myntra.com/shop"
]

print("URL Normalization Test Results:")
print("-" * 80)
for url in test_urls:
    normalized = normalize_url(url)
    print(f"Original:   {url}")
    print(f"Normalized: {normalized}")
    print("-" * 80)