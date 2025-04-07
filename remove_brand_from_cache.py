import json
from paths import FETCHED_URLS_JSON

def remove_brand_urls(brand_name, brand_domain):
    # Load the cache
    try:
        with open(FETCHED_URLS_JSON, "r") as f:
            cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Cache file not found or invalid JSON")
        return

    # Count original entries
    original_count = len(cache)
    
    # Remove brand URLs
    cache = {k: v for k, v in cache.items() if not k.startswith(brand_domain)}
    
    # Count removed entries
    removed_count = original_count - len(cache)
    
    # Save the updated cache
    with open(FETCHED_URLS_JSON, "w") as f:
        json.dump(cache, f, indent=4)
    
    print(f"Removed {removed_count} {brand_name} URLs from cache")
    print(f"Cache now contains {len(cache)} entries")

if __name__ == "__main__":
    remove_brand_urls("Prosestories", "https://prosestories.com")
