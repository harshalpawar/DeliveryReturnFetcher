from src.scrape import jina_reader
from logging_config import log as logger

test_urls = ['https://www.nike.com/in/help/a/bank-transaction-fees', 'https://www.nike.com/in/help/a/how-to-return', 'https://www.nike.com/in/membership', 'https://www.nike.com/in/nike-by-you', 'https://www.nike.com/in/retail/s/nike-bellevue-square', 'https://www.nike.com/in/jordan', 'https://www.nike.com/in/t/air-more-uptempo-96-shoes-gDWSHg', 'https://www.nike.com/in/membership/shipping', 'https://www.nike.com/in/orders/details', 'https://www.nike.com/in/retail/s/nike-well-collective-south-windsor', 'https://www.nike.com/in/help/a/india-consumer-care-policy', 'https://www.nike.com/in/help/a/verify-passport', 'https://www.nike.com/in/help/a/shipping-delivery', 'https://www.nike.com/in/help/a/nike-by-you-return-gs', 'https://www.nike.com/in/help/a/returns-policy-gs']

def test_jina_reader():
    try:
        urls = test_urls
        content = jina_reader(urls)
        logger.info(f"Content: {content}")
    except Exception as e:
        logger.error(f"Error in jina_reader: {e}")

if __name__ == "__main__":
    test_jina_reader()


