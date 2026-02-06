import os
import logging
from main_scheduler import process_daily_digest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Triggering Daily Digest from CLI...")
    success, msg = process_daily_digest()
    if success:
        logger.info(f"SUCCESS: {msg}")
        exit(0)
    else:
        logger.error(f"FAILURE: {msg}")
        exit(1)
