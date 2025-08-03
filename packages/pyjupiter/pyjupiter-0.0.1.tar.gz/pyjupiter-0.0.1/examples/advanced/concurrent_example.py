#!/usr/bin/env python3
"""
Advanced example: Concurrent requests with async Jupiter SDK
"""

import asyncio
import logging
import time
from typing import Any

from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_token_safety(client: AsyncUltraApiClient, mint: str) -> dict[str, Any]:
    """Check a single token for safety warnings"""
    try:
        response = await client.shield(mints=[mint])
        return {
            "mint": mint,
            "warnings": response.get("warnings", {}).get(mint, []),
            "success": True,
        }
    except Exception as e:
        return {"mint": mint, "error": str(e), "success": False}


async def concurrent_token_check():
    """Check multiple tokens concurrently"""

    # Popular Solana tokens
    tokens = {
        "So11111111111111111111111111111111111111112": "WSOL",
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
        "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
        "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs": "ETH",
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263": "BONK",
        "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3": "PYTH",
        "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL": "JTO",
    }

    logger.info(f"Checking {len(tokens)} tokens concurrently...")

    client = AsyncUltraApiClient()
    start_time = time.time()

    try:
        # Create tasks for all tokens
        tasks = [check_token_safety(client, mint) for mint in tokens]

        # Execute all requests concurrently
        results = await asyncio.gather(*tasks)

        # Process results
        logger.info("=== Token Safety Check Results ===")

        safe_tokens = []
        warning_tokens = []

        for result in results:
            if result["success"]:
                token_name = tokens.get(result["mint"], "Unknown")

                if result["warnings"]:
                    warning_tokens.append((token_name, result))
                    logger.warning(f"⚠️  {token_name} ({result['mint'][:8]}...)")
                    for warning in result["warnings"]:
                        logger.warning(f"   - {warning.get('type')}: {warning.get('message')}")
                else:
                    safe_tokens.append(token_name)
                    logger.info(f"✅ {token_name} ({result['mint'][:8]}...) - No warnings")
            else:
                logger.error(f"❌ Failed to check {result['mint']}: {result.get('error')}")

        # Summary
        elapsed = time.time() - start_time
        logger.info("=== Summary ===")
        logger.info(f"Total tokens checked: {len(tokens)}")
        logger.info(f"Safe tokens: {len(safe_tokens)}")
        logger.info(f"Tokens with warnings: {len(warning_tokens)}")
        logger.info(f"Time elapsed: {elapsed:.2f} seconds")
        logger.info(f"Average time per request: {elapsed / len(tokens):.3f} seconds")

    finally:
        await client.close()


async def batch_balance_check():
    """Check balances for multiple addresses concurrently"""

    # Example addresses (you can replace with real ones)
    addresses = [
        "11111111111111111111111111111111",  # System program
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token program
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC mint
    ]

    logger.info(f"Checking balances for {len(addresses)} addresses...")

    client = AsyncUltraApiClient()

    async def get_balance(address: str):
        try:
            balance = await client.balances(address)
            return {"address": address, "balance": balance, "success": True}
        except Exception as e:
            return {"address": address, "error": str(e), "success": False}

    try:
        # Check all balances concurrently
        tasks = [get_balance(addr) for addr in addresses]
        results = await asyncio.gather(*tasks)

        # Display results
        for result in results:
            success = result.get("success", False)
            if success is True:
                address = str(result.get("address", ""))
                if len(address) >= 16:
                    logger.info(f"Address: {address[:16]}...")
                else:
                    logger.info(f"Address: {address}...")
                balance = result.get("balance")
                if balance and isinstance(balance, dict):
                    for token, details in balance.items():
                        if isinstance(details, dict):
                            logger.info(f"  {token}: {details.get('uiAmount', 0)}")
                else:
                    logger.info("  No balances found")
            else:
                address = str(result.get("address", "Unknown"))
                error = str(result.get("error", "Unknown error"))
                logger.error(f"Failed to check {address}: {error}")

    finally:
        await client.close()


async def rate_limited_requests():
    """Example of rate-limited concurrent requests"""

    logger.info("=== Rate-Limited Concurrent Requests ===")

    # Semaphore to limit concurrent requests
    max_concurrent = 3
    semaphore = asyncio.Semaphore(max_concurrent)

    async def rate_limited_request(client: AsyncUltraApiClient, mint: str, delay: float):
        async with semaphore:  # Acquire semaphore
            logger.info(f"🔄 Checking {mint[:8]}...")
            await asyncio.sleep(delay)  # Simulate some processing
            result = await client.shield(mints=[mint])
            logger.info(f"✓ Completed {mint[:8]}...")
            return result

    client = AsyncUltraApiClient()

    mints = [
        "So11111111111111111111111111111111111111112",
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs",
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    ]

    try:
        msg = f"Processing {len(mints)} requests with max {max_concurrent} concurrent..."
        logger.info(msg)

        tasks = [rate_limited_request(client, mint, 0.5) for mint in mints]

        start = time.time()
        await asyncio.gather(*tasks)
        elapsed = time.time() - start

        logger.info(f"Completed in {elapsed:.2f} seconds")
        logger.info(f"(Would take {len(mints) * 0.5:.2f} seconds sequentially)")

    finally:
        await client.close()


async def main():
    """Run all examples"""

    logger.info("=== Jupiter SDK Concurrent Operations Demo ===")

    # Example 1: Concurrent token safety checks
    await concurrent_token_check()

    # Example 2: Batch balance checks
    # await batch_balance_check()

    # Example 3: Rate-limited requests
    await rate_limited_requests()


if __name__ == "__main__":
    asyncio.run(main())
