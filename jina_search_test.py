from src.search import jina_search
from logging_config import log as logger

def test_jina_search():
    try:
        brand_name = "Nike"
        brand_domain = "https://nike.com/in/"
        urls = jina_search(brand_name, brand_domain)
        logger.info(f"Found URLs: {urls}")
    except Exception as e:
        logger.error(f"Error in jina_search: {e}")

if __name__ == "__main__":
    test_jina_search()