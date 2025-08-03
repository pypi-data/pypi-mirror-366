#!/usr/bin/env python3
"""
Advanced example: Using proxy and client configurations with Jupiter SDK

This example demonstrates various client configurations supported by curl_cffi AsyncSession:
- Basic client configuration (timeout, SSL verification)
- Proxy support (HTTP/HTTPS and SOCKS5)
- Environment proxy settings

Note: Custom DNS resolution (resolve, dns_servers) is not directly supported
by curl_cffi AsyncSession and must be handled at the system/OS level.
"""

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


async def example_with_proxy():
    """Example using SOCKS5 proxy"""

    # Configure SOCKS5 proxy (e.g., for Tor)
    # Note: You need to have a SOCKS5 proxy running
    # Supported proxy formats:
    # - HTTP: "http://proxy.example.com:8080"
    # - HTTPS: "https://proxy.example.com:8080"
    # - SOCKS5: "socks5://127.0.0.1:1080"
    # - With auth: "socks5://user:pass@proxy.example.com:1080"
    proxies = {"https": "socks5://127.0.0.1:1080"}

    logger.info("Creating client with SOCKS5 proxy...")
    client = AsyncUltraApiClient(
        client_kwargs={
            "proxies": proxies,
            "timeout": 30,  # 30 seconds timeout
            "verify": True,  # Verify SSL certificates even through proxy
        }
    )

    try:
        # Test the connection
        logger.info("Fetching shield information through proxy...")

        wsol_mint = "So11111111111111111111111111111111111111112"
        shield_response = await client.shield(mints=[wsol_mint])

        logger.info("✓ Successfully connected through proxy!")
        logger.info(f"Response type: {type(shield_response)}")

    except Exception as e:
        logger.error(f"✗ Error occurred: {e}")
        logger.error("Make sure your proxy is running and accessible")

    finally:
        await client.close()


async def example_with_basic_client():
    """Example using basic client configuration"""

    logger.info("Creating client with basic configuration...")

    # Basic client configuration with timeout and SSL verification
    # curl_cffi AsyncSession supports these parameters:
    # - timeout: Connection timeout
    # - verify: SSL certificate verification
    # - trust_env: Use environment proxy settings
    # - impersonate: Browser fingerprinting
    client = AsyncUltraApiClient(
        client_kwargs={
            "timeout": 30,  # 30 seconds timeout
            "verify": True,  # Verify SSL certificates
            "trust_env": True,  # Use environment proxy settings
        }
    )

    try:
        logger.info("Testing basic client connection...")

        # Test with shield endpoint (doesn't require private key)
        wsol_mint = "So11111111111111111111111111111111111111112"
        shield_response = await client.shield(mints=[wsol_mint])
        logger.info("✓ Shield endpoint working correctly!")
        logger.info(f"Shield response type: {type(shield_response)}")

        # Only test public key if PRIVATE_KEY is available
        try:
            public_key = await client.get_public_key()
            logger.info(f"✓ Public key retrieved: {public_key}")
        except ValueError as pk_error:
            logger.info(f"Info: Private key not available: {pk_error}")
            logger.info("Set PRIVATE_KEY environment variable to test key functionality")

    except Exception as e:
        logger.error(f"✗ Error occurred: {e}")

    finally:
        await client.close()


async def example_with_http_proxy():
    """Example using HTTP/HTTPS proxy"""

    # Configure HTTP proxy with authentication
    # Note: Replace with your actual proxy credentials
    proxies = {
        "http": "http://username:password@proxy.example.com:8080",
        "https": "http://username:password@proxy.example.com:8080",
    }

    logger.info("Creating client with HTTP proxy...")
    client = AsyncUltraApiClient(
        client_kwargs={
            "proxies": proxies,
            "verify": True,  # Verify SSL certificates
            "timeout": 30,  # 30 seconds timeout
            "trust_env": False,  # Don't use environment proxy settings
        }
    )

    try:
        logger.info("Testing connection through HTTP proxy...")

        # Test with a simple request
        usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        shield_response = await client.shield(mints=[usdc_mint])

        logger.info("✓ Successfully connected through HTTP proxy!")
        logger.info(f"Response type: {type(shield_response)}")

    except Exception as e:
        logger.error(f"✗ Error occurred: {e}")
        logger.error("Check your proxy settings and credentials")

    finally:
        await client.close()


async def main():
    """Run examples"""

    # Load environment variables
    load_environment()

    logger.info("=== Jupiter SDK Advanced Features Demo ===")

    # Example 1: Basic client configuration
    await example_with_basic_client()

    logger.info("=" * 50)

    # Example 2: Proxy support
    # Uncomment to test with a real proxy
    # await example_with_proxy()
    # await example_with_http_proxy()

    logger.info("Note: Proxy examples are commented out.")
    logger.info("To test them, ensure you have a proxy running and uncomment the code.")


if __name__ == "__main__":
    asyncio.run(main())
