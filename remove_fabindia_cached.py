import json
from paths import FETCHED_URLS_JSON

def remove_fabindia_urls():
    # Load the cache
    try:
        with open(FETCHED_URLS_JSON, "r") as f:
            cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Cache file not found or invalid JSON")
        return

    # Count original entries
    original_count = len(cache)
    
    # Remove Fabindia URLs
    cache = {k: v for k, v in cache.items() if not k.startswith("https://fabindia.com")}
    
    # Count removed entries
    removed_count = original_count - len(cache)
    
    # Save the updated cache
    with open(FETCHED_URLS_JSON, "w") as f:
        json.dump(cache, f, indent=4)
    
    print(f"Removed {removed_count} Fabindia URLs from cache")
    print(f"Cache now contains {len(cache)} entries")

if __name__ == "__main__":
    remove_fabindia_urls()
