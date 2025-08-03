import asyncio
import logging

from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    client = AsyncUltraApiClient()

    # WSOL and USDC mints
    wsol_mint = "So11111111111111111111111111111111111111112"
    usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

    try:
        shield_response = await client.shield(mints=[wsol_mint, usdc_mint])

        logger.info("Shield API Response (Async):")
        if shield_response.get("warnings"):
            for mint, warnings in shield_response["warnings"].items():
                logger.warning(f"Mint: {mint}")
                for warning in warnings:
                    logger.warning(f"  - Type: {warning.get('type')}")
                    logger.warning(f"    Message: {warning.get('message')}")
        else:
            logger.info("No warnings returned for provided mints")

    except Exception as e:
        logger.error("Error occurred while fetching shield information:", str(e))
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
