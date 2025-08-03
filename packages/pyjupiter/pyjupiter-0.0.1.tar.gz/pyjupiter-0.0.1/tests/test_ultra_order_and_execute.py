import logging

import pytest
from utils import load_environment

from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient, UltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import (
    UltraOrderRequest,
)

logger = logging.getLogger(__name__)


@pytest.mark.requires_private_key
def test_ultra_get_order_and_execute() -> None:
    """
    Test the sync UltraApiClient's ability to fetch an order and execute it.
    """
    load_environment()
    client = UltraApiClient()

    order_request = UltraOrderRequest(
        input_mint="So11111111111111111111111111111111111111112",  # WSOL
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        amount=10000000,  # 0.01 WSOL
        taker=client.get_public_key(),
    )

    try:
        client_response = client.order_and_execute(order_request)
        signature = str(client_response["signature"])
        assert signature is not None, "Transaction signature is missing or invalid."

        logger.info("")
        logger.info("Order and Execute API Response:")
        logger.info(f"  - Transaction Signature: {signature}")
        logger.info(f"  - View on Solscan: https://solscan.io/tx/{signature}")

    except Exception as e:
        logger.info("Error occurred while processing the order:", str(e))
    finally:
        client.close()


@pytest.mark.requires_private_key
@pytest.mark.asyncio
async def test_async_ultra_get_order_and_execute() -> None:
    """
    Test the async UltraApiClient's ability to fetch an order and execute it.
    """
    load_environment()
    client = AsyncUltraApiClient()

    order_request = UltraOrderRequest(
        input_mint="So11111111111111111111111111111111111111112",  # WSOL
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        amount=10000000,  # 0.01 WSOL
        taker=await client.get_public_key(),
    )

    try:
        client_response = await client.order_and_execute(order_request)
        signature = str(client_response["signature"])
        assert signature is not None, "Transaction signature is missing or invalid."

        logger.info("")
        logger.info("Async Order and Execute API Response:")
        logger.info(f"  - Transaction Signature: {signature}")
        logger.info(f"  - View on Solscan: https://solscan.io/tx/{signature}")

    except Exception as e:
        logger.info("Error occurred while processing the async order:", str(e))
    finally:
        await client.close()
