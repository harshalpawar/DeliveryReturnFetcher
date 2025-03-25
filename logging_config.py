from loguru import logger
import sys

# Configure logging only once
logger.remove()  # Remove default handler
logger.add(sys.stderr, level="INFO")  # Console output
logger.add("logs/pipeline.log", rotation="500 MB", level="INFO")  # File output

# Export the configured logger
log = logger
