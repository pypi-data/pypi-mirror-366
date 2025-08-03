import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils import load_environment

from pyjupiter.clients.ultra_api_client import UltraApiClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_environment()
client = UltraApiClient()

address = client.get_public_key()

try:
    balances_response = client.balances(str(address))

    logger.info("Balances API Response:")
    for token, details in balances_response.items():
        logger.info(f"Token: {token}")
        logger.info(f"  - Amount: {details['amount']}")
        logger.info(f"    UI Amount: {details['uiAmount']}")
        logger.info(f"    Slot: {details['slot']}")
        logger.info(f"    Is Frozen: {details['isFrozen']}")

except Exception as e:
    logger.error("Error occurred while fetching balances:", str(e))
finally:
    client.close()
