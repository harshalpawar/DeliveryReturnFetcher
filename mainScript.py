import argparse, json, sys, os
from src import search, scrape, response
from paths import BRAND_INPUT_JSON, BRAND_OUTPUT_JSON
from logging_config import log as logger

# parse arguments from command line
def parse_arguments():
    parser = argparse.ArgumentParser(description="Extract policy information from fashion brands in India")
    parser.add_argument("--brand", help="Specify a single brand to process")
    parser.add_argument("--skip-done", action="store_true", help="Skip brands already in output file")
    parser.add_argument("--pause-mode", action="store_true", help="Pause after each stage for manual verification")
    parser.add_argument("--desc", help="Description of the run", default="")
    return parser.parse_args()

# input: brand_name, brand_domain
# output: brand policy information
# description: process a single brand
# if there is an error, return None
def process_brand(brand_name, brand_domain, pause_mode=False):
    logger.info(f"Processing brand: {brand_name}")
    try:
        # search for policy pages
        urls = search.jina_search(brand_name, brand_domain)
        logger.info(f"Found URLs: {urls}")
        if pause_mode:
            input("Press Enter to continue to scrape stage...")
        # scrape the policy pages
        scraped_content = scrape.jina_reader(urls, brand_name)
        # logger.info(f"Scraped content: {scraped_content}")
        if pause_mode:
            input("Press Enter to continue to gemini stage...")
        # extract policy information
        policy_info = response.gemini_llm(scraped_content, brand_name)
        logger.info(f"Extracted policy information for {brand_name}: {policy_info}")
        return policy_info

    except Exception as e:
        logger.error(f"Error processing brand {brand_name}: {e}")
        return None

# input: brands, existing_data, args
# output: None
# description: calls process_brand for each brand and writes the output to the output file
def process_brands(brands, existing_data, args):
    logger.info(f"Processing {len(brands)} brands")

    for brand_name, brand_domain in brands.items():
        logger.info("-" * 40) # Separator line
        # Check if the brand is already processed and skip if --skip-done is used
        if args.skip_done and brand_name in existing_data:
            logger.info(f"Skipping {brand_name} (already processed)")
            continue
        result = process_brand(brand_name, brand_domain, pause_mode=args.pause_mode)
        if result:
            existing_data[brand_name] = result
        if args.pause_mode:
            input("Press Enter to continue to next brand...")

    #Write all of the code from existing_data, overwriting the existing file
    with open(BRAND_OUTPUT_JSON, "w") as f:
        json.dump(existing_data, f, indent=4)
    logger.info(f"Processed {len(brands)} brands")

# input: brand_input.json, brand_output.json
# output: brands, existing_data
# description: load the data from the input and output files into lists
# exit if there is an error
def load_data(input_file, output_file):
    try:
        with open(input_file, "r") as f:
            brands = json.load(f)
    except Exception as e:
        logger.error(f"Error loading {input_file}: {e}")
        sys.exit(1)

    # Create the output file if it does not exist
    if not os.path.exists(output_file):
        logger.info(f"{output_file} does not exist. Creating a new file.")
        with open(output_file, "w") as f:
            json.dump({}, f)  # Initialize with an empty dictionary

    try:
        with open(output_file, "r") as f:
            existing_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading {output_file}: {e}")
        existing_data = {}

    return brands, existing_data

# handle single brand or all brands
def main():    
    brands, existing_data = load_data(BRAND_INPUT_JSON, BRAND_OUTPUT_JSON)

    args = parse_arguments()
    logger.info("-" * 40) # Separator line
    logger.info("Starting pipeline")
    # If specific test to run with details
    if args.desc:
        logger.info(f"Description: {args.desc}")
    logger.info("-" * 40) # Separator line  

    if args.brand:
        if args.brand not in brands:
            print(f"Brand {args.brand} not found in brand_input.json")
        else:
            process_brands({args.brand: brands[args.brand]}, existing_data, args) 
    else:
        process_brands(brands, existing_data, args)

    logger.info("-" * 40) # Separator line
    logger.info("Pipeline completed")
    logger.info("-" * 40) # Separator line  

if __name__ == "__main__":
    main()
