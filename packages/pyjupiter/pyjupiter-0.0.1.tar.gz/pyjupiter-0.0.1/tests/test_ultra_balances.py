import logging

import pytest
from utils import load_environment

from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient, UltraApiClient

logger = logging.getLogger(__name__)


@pytest.mark.requires_private_key
def test_ultra_get_balances() -> None:
    """
    Test the sync UltraApiClient balances method.
    """
    load_environment()
    client = UltraApiClient()

    address = client.get_public_key()

    try:
        balances_response = client.balances(str(address))
        assert "SOL" in balances_response, "Response does not contain 'SOL' key."

        logger.info("")
        logger.info("Balances API Response:")
        for token, details in balances_response.items():
            logger.info(f"Token: {token}")
            logger.info(f"  - Amount: {details['amount']}")
            logger.info(f"    UI Amount: {details['uiAmount']}")
            logger.info(f"    Slot: {details['slot']}")
            logger.info(f"    Is Frozen: {details['isFrozen']}")

    except Exception as e:
        logger.info("Error occurred while fetching balances:", str(e))
    finally:
        client.close()


@pytest.mark.requires_private_key
@pytest.mark.asyncio
async def test_async_ultra_get_balances() -> None:
    """
    Test the async UltraApiClient balances method.
    """
    load_environment()
    client = AsyncUltraApiClient()

    address = await client.get_public_key()

    try:
        balances_response = await client.balances(str(address))
        assert "SOL" in balances_response, "Response does not contain 'SOL' key."

        logger.info("")
        logger.info("Async Balances API Response:")
        for token, details in balances_response.items():
            logger.info(f"Token: {token}")
            logger.info(f"  - Amount: {details['amount']}")
            logger.info(f"    UI Amount: {details['uiAmount']}")
    except Exception as e:
        logger.info("Error occurred while fetching async balances:", str(e))
    finally:
        await client.close()
