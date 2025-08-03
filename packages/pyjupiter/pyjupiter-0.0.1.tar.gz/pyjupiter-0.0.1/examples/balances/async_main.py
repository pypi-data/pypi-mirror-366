import asyncio
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils import load_environment

from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    load_environment()

    client = AsyncUltraApiClient()

    address = await client.get_public_key()

    try:
        balances_response = await client.balances(str(address))

        logger.info("Balances API Response (Async):")
        for token, details in balances_response.items():
            logger.info(f"Token: {token}")
            logger.info(f"  - Amount: {details['amount']}")
            logger.info(f"    UI Amount: {details['uiAmount']}")
            logger.info(f"    Slot: {details['slot']}")
            logger.info(f"    Is Frozen: {details['isFrozen']}")

    except Exception as e:
        logger.error("Error occurred while fetching balances:", str(e))
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
