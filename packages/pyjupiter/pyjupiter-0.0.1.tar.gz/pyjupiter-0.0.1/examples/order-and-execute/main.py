import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils import load_environment

from pyjupiter.clients.ultra_api_client import UltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_environment()
client = UltraApiClient()

# Example swap: 0.01 WSOL -> USDC
# NOTE: This requires your wallet to have at least 0.01 WSOL tokens
# You can get WSOL by wrapping SOL or by receiving WSOL from other sources
order_request = UltraOrderRequest(
    input_mint="So11111111111111111111111111111111111111112",  # WSOL
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    amount=10000000,  # 0.01 WSOL (10,000,000 lamports)
    taker=client.get_public_key(),
)

logger.info("Attempting to swap 0.01 WSOL to USDC")
logger.info(f"Wallet address: {client.get_public_key()}")
logger.info("Please ensure this wallet has at least 0.01 WSOL tokens before running this example")

try:
    # First check what the order method returns to handle insufficient balance
    logger.info("Getting order from Jupiter Ultra API...")
    order_response = client.order(order_request)

    # Check if there's an error (like insufficient balance)
    if order_response.get("errorMessage"):
        logger.error(f"API Error: {order_response.get('errorMessage')}")
        logger.info(f"Requested amount: {order_request.amount} lamports ({order_request.amount / 1e9} SOL)")
        logger.info("Please ensure your wallet has sufficient balance for the swap.")
        logger.info(f"Wallet address: {client.get_public_key()}")
        raise ValueError(f"API Error: {order_response.get('errorMessage')}")

    # If no transaction data, something went wrong
    if not order_response.get("transaction"):
        logger.error("No transaction data returned from API, but no error message provided")
        raise ValueError("No transaction data returned from API")

    logger.info(f"Order successful - Request ID: {order_response.get('requestId')}")

    # Now execute the full order and execute
    client_response = client.order_and_execute(order_request)
    signature = str(client_response["signature"])

    logger.info("Order and Execute API Response:")
    logger.info(f"  - Status: {client_response.get('status')}")
    if client_response.get("status") == "Failed":
        logger.error(f"  - Code: {client_response.get('code')}")
        logger.error(f"  - Error: {client_response.get('error')}")

    logger.info(f"  - Transaction Signature: {signature}")
    logger.info(f"  - View on Solscan: https://solscan.io/tx/{signature}")

except Exception as e:
    logger.error("Error occurred while processing the swap: %s", str(e))
finally:
    client.close()
