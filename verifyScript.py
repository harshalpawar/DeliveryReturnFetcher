import json
from src import search, scrape, response
from paths import BRAND_INPUT_JSON, VERIFICATION_RESULTS, HUMAN_DATA
from logging_config import log as logger

def process_brand_for_verification(brand_name, brand_domain):
    """
    Process a single brand and verify its policy information against human data.
    """
    logger.info(f"Processing brand for verification: {brand_name}")
    try:
        # Load human-verified data
        with open(HUMAN_DATA, "r") as f:
            human_data = json.load(f)
            
        if brand_name not in human_data:
            logger.error(f"No human-verified data found for {brand_name}")
            return None

        # search for policy pages
        urls = search.jina_search(brand_name, brand_domain)
        logger.info(f"Found URLs: {urls}")
        
        # scrape the policy pages
        scraped_content = scrape.jina_reader(urls, brand_name)
            
        # verify against human data
        verification_result = response.verify_gemini(scraped_content, human_data[brand_name], brand_name)
        logger.info(f"Verification result for {brand_name}: {verification_result}")
        return verification_result

    except Exception as e:
        logger.error(f"Error processing brand {brand_name}: {e}")
        return None

def process_brands_verification(brands):
    """
    Process all brands and write verification results to a new file.
    """
    logger.info(f"Starting verification for {len(brands)} brands")
    verification_results = {}

    for brand_name, brand_domain in brands.items():
        logger.info("-" * 40)  # Separator line
        result = process_brand_for_verification(brand_name, brand_domain)
        if result:
            verification_results[brand_name] = result

    # Write verification results to a new file
    with open(VERIFICATION_RESULTS, "w") as f:
        json.dump(verification_results, f, indent=4)

    logger.info(f"Completed verification for {len(verification_results)} brands")
    return verification_results

def main():
    logger.info("-" * 40)
    logger.info("Starting verification pipeline")
    logger.info("-" * 40)

    # Load brand data
    try:
        with open(BRAND_INPUT_JSON, "r") as f:
            brands = json.load(f)
    except Exception as e:
        logger.error(f"Error loading {BRAND_INPUT_JSON}: {e}")
        return

    # Process all brands
    results = process_brands_verification(brands)
    
    logger.info("-" * 40)
    logger.info("Verification pipeline completed")
    logger.info("-" * 40)

if __name__ == "__main__":
    main() 