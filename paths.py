import os

# Absolute path to project root
PROJECT_HOME = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(PROJECT_HOME, ".env")
BRAND_INPUT_JSON = os.path.join(PROJECT_HOME, "data", "brand_input.json")
BRAND_OUTPUT_JSON = os.path.join(PROJECT_HOME, "data", "brand_output.json")
FETCHED_URLS_JSON = os.path.join(PROJECT_HOME, "data", "fetched_urls.json")
HUMAN_DATA = os.path.join(PROJECT_HOME, "data", "human_data.json")
VERIFICATION_RESULTS = os.path.join(PROJECT_HOME, "data", "verification_results.json")
