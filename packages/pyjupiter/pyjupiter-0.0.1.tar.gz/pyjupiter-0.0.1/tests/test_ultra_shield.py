import logging

import pytest
from utils import load_environment

from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient, UltraApiClient

logger = logging.getLogger(__name__)


def test_ultra_shield() -> None:
    """
    Test the sync UltraApiClient shield method.
    """
    load_environment()
    client = UltraApiClient()

    # WSOL and USDC mints
    wsol_mint = "So11111111111111111111111111111111111111112"
    usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

    try:
        shield_response = client.shield(mints=[wsol_mint, usdc_mint])
        assert "warnings" in shield_response, "Response does not contain 'warnings' key."

        logger.info("")
        logger.info("Shield API Response:")
        if shield_response.get("warnings"):
            for mint, warnings in shield_response["warnings"].items():
                logger.info(f"Mint: {mint}")
                for warning in warnings:
                    logger.info(f"  - Type: {warning.get('type')}")
                    logger.info(f"    Message: {warning.get('message')}")
        else:
            logger.info("No warnings returned for provided mints")

    except Exception as e:
        logger.info("Error occurred while fetching shield information:", str(e))
    finally:
        client.close()


@pytest.mark.asyncio
async def test_async_ultra_shield() -> None:
    """
    Test the async UltraApiClient shield method.
    """
    load_environment()
    client = AsyncUltraApiClient()

    # WSOL and USDC mints
    wsol_mint = "So11111111111111111111111111111111111111112"
    usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

    try:
        shield_response = await client.shield(mints=[wsol_mint, usdc_mint])
        assert "warnings" in shield_response, "Response does not contain 'warnings' key."

        logger.info("")
        logger.info("Async Shield API Response:")
        if shield_response.get("warnings"):
            for mint, warnings in shield_response["warnings"].items():
                logger.info(f"Mint: {mint}")
                for warning in warnings:
                    logger.info(f"  - Type: {warning.get('type')}")
                    logger.info(f"    Message: {warning.get('message')}")
    except Exception as e:
        logger.info("Error occurred while fetching async shield information:", str(e))
    finally:
        await client.close()
