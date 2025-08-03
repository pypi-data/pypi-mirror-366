# **Jupiter Python SDK**

[![PyPI version](https://badge.fury.io/py/pyjupiter.svg)](https://badge.fury.io/py/pyjupiter)
[![Python](https://img.shields.io/pypi/pyversions/pyjupiter.svg)](https://pypi.org/project/pyjupiter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance, async-first Python SDK for seamless interaction with the Jupiter Ultra API, powered by `curl_cffi`
for maximum speed and flexibility.

With Ultra API, you don't need to manage or connect to any RPC endpoints, or deal with complex configurations.
Everything from getting quotes to transaction execution happens directly through a powerful API.

Or as we like to say around here: **"RPCs are for NPCs."**

## **Table of Contents**

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)
- [Advanced Usage](#advanced-usage)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [Resources](#resources)

## **Features**

- 🚀 **High Performance**: Built on `curl_cffi` for blazing-fast HTTP requests
- 🔄 **Async/Sync Support**: Both asynchronous and synchronous clients available
- 🛡️ **Token Safety**: Built-in shield API for token security warnings
- 💰 **Balance Checking**: Easy balance retrieval for any Solana address
- 🔧 **Advanced Configuration**: Support for proxies, custom DNS, and more
- 📦 **Type Safety**: Full type hints with Pydantic models
- 🎯 **Zero Configuration**: Works out of the box with minimal setup

## **Installation**

install [uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation)

```bash
uv add pyjupiter
```

### Requirements

- Python 3.9 or higher
- A Solana wallet private key (for transaction signing)

## **Quick Start**

### Async Example

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

async def main():
    # Initialize the async client
    client = AsyncUltraApiClient()

    # Create a swap order
    order_request = UltraOrderRequest(
        input_mint="So11111111111111111111111111111111111111112",  # WSOL
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        amount=10000000,  # 0.01 WSOL
        taker=await client.get_public_key(),
    )

    try:
        # Execute the swap
        response = await client.order_and_execute(order_request)
        print(f"Transaction: https://solscan.io/tx/{response['signature']}")
    finally:
        await client.close()

asyncio.run(main())
```

### Sync Example

```python
from pyjupiter.clients.ultra_api_client import UltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

# Initialize the sync client
client = UltraApiClient()

# Create and execute a swap
order_request = UltraOrderRequest(
    input_mint="So11111111111111111111111111111111111111112",  # WSOL
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    amount=10000000,  # 0.01 WSOL
    taker=client.get_public_key(),
)

response = client.order_and_execute(order_request)
print(f"Transaction: https://solscan.io/tx/{response['signature']}")
client.close()
```

## **Configuration**

### Environment Variables

Set up your private key as an environment variable:

```bash
# Base58 format (standard Solana format)
export PRIVATE_KEY=your_base58_private_key_here

# OR as a uint8 array
export PRIVATE_KEY=[10,229,131,132,213,96,74,22,...]
```

### Client Configuration

```python
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

# With API key (for enhanced access)
client = AsyncUltraApiClient(
    api_key="YOUR_API_KEY",  # Get from https://portal.jup.ag/onboard
    private_key_env_var="CUSTOM_PRIVATE_KEY"  # Custom env var name
)

# With custom client configuration
client = AsyncUltraApiClient(
    client_kwargs={
        "timeout": 30,  # 30 seconds timeout
        "verify": True,  # SSL verification
    }
)
```

## **API Reference**

### UltraApiClient / AsyncUltraApiClient

The main client classes for interacting with the Jupiter Ultra API.

#### Methods

##### `order(request: UltraOrderRequest) -> dict`

Get a swap order from the Jupiter Ultra API.

**Parameters:**

- `request`: An `UltraOrderRequest` object containing:
  - `input_mint` (str): Input token mint address
  - `output_mint` (str): Output token mint address
  - `amount` (int): Amount in smallest unit (e.g., lamports for SOL)
  - `taker` (str, optional): Taker's public key
  - `referral_account` (str, optional): Referral account address
  - `referral_fee` (int, optional): Referral fee in basis points

**Returns:** Dict containing order details including `requestId` and `transaction`

##### `execute(request: UltraExecuteRequest) -> dict`

Execute a previously created order.

**Parameters:**

- `request`: An `UltraExecuteRequest` object containing:
  - `request_id` (str): The request ID from the order
  - `signed_transaction` (str): Base64-encoded signed transaction

**Returns:** Dict containing execution result including `signature` and `status`

##### `order_and_execute(request: UltraOrderRequest) -> dict`

Create and execute an order in a single call.

**Parameters:**

- `request`: Same as `order()` method

**Returns:** Dict containing execution result including `signature` and `status`

##### `balances(address: str) -> dict`

Get token balances for a Solana address.

**Parameters:**

- `address` (str): Solana public key address

**Returns:** Dict mapping token symbols to balance details:

```python
{
    "SOL": {
        "amount": "100000000",
        "uiAmount": 0.1,
        "slot": 123456,
        "isFrozen": False
    }
}
```

##### `shield(mints: list[str]) -> dict`

Check tokens for safety warnings.

**Parameters:**

- `mints` (list[str]): List of token mint addresses to check

**Returns:** Dict containing warnings for each mint:

```python
{
    "warnings": {
        "mint_address": [
            {
                "type": "warning_type",
                "message": "Warning description"
            }
        ]
    }
}
```

### Models

#### UltraOrderRequest

Pydantic model for creating swap orders.

```python
UltraOrderRequest(
    input_mint="So11111111111111111111111111111111111111112",
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    amount=10000000,
    taker="your_public_key",
    referral_account="optional_referral_address",
    referral_fee=50  # 0.5% in basis points
)
```

#### UltraExecuteRequest

Pydantic model for executing orders.

```python
UltraExecuteRequest(
    request_id="order_request_id",
    signed_transaction="base64_encoded_signed_transaction"
)
```

## **Usage Examples**

### Check Token Balances

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

async def check_balances():
    client = AsyncUltraApiClient()

    # Get your wallet address
    address = await client.get_public_key()

    # Fetch balances
    balances = await client.balances(address)

    for token, details in balances.items():
        print(f"{token}: {details['uiAmount']} (frozen: {details['isFrozen']})")

    await client.close()

asyncio.run(check_balances())
```

### Check Token Safety

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

async def check_token_safety():
    client = AsyncUltraApiClient()

    # Popular tokens to check
    mints = [
        "So11111111111111111111111111111111111111112",  # WSOL
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
    ]

    shield_response = await client.shield(mints)

    for mint, warnings in shield_response.get("warnings", {}).items():
        if warnings:
            print(f"⚠️ {mint} has warnings:")
            for warning in warnings:
                print(f"  - {warning['type']}: {warning['message']}")
        else:
            print(f"✅ {mint} appears safe")

    await client.close()

asyncio.run(check_token_safety())
```

### Concurrent Operations

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

async def concurrent_operations():
    client = AsyncUltraApiClient()

    # Define multiple tokens to check
    tokens = [
        "So11111111111111111111111111111111111111112",
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    ]

    # Create tasks for concurrent execution
    tasks = []
    for token in tokens:
        task = client.shield([token])
        tasks.append(task)

    # Execute all requests concurrently
    results = await asyncio.gather(*tasks)

    # Process results
    for token, result in zip(tokens, results):
        print(f"Token {token}: {result}")

    await client.close()

asyncio.run(concurrent_operations())
```

## **Best Practices**

### 1. Always Close Clients

```python
# Using try/finally
client = AsyncUltraApiClient()
try:
    # Your code here
    pass
finally:
    await client.close()

# Or using async context manager (if implemented)
async with AsyncUltraApiClient() as client:
    # Your code here
    pass
```

### 2. Error Handling

```python
try:
    response = await client.order_and_execute(order_request)

    if response.get("status") == "Failed":
        print(f"Transaction failed: {response.get('error')}")
    else:
        print(f"Success: {response['signature']}")

except Exception as e:
    print(f"Error occurred: {e}")
```

### 3. Rate Limiting

```python
import asyncio

# Use semaphore to limit concurrent requests
semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests

async def rate_limited_request(client, mint):
    async with semaphore:
        return await client.shield([mint])
```

### 4. Retry Logic

```python
import asyncio
from typing import Optional

async def retry_request(func, max_retries=3, delay=1.0):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(delay * (attempt + 1))
```

### 5. Token Amount Calculations

```python
# Always work with the smallest unit (lamports for SOL)
sol_amount = 0.01  # SOL
lamports = int(sol_amount * 10**9)  # Convert to lamports

# For other tokens, check their decimals
usdc_amount = 10.0  # USDC
usdc_smallest_unit = int(usdc_amount * 10**6)  # USDC has 6 decimals
```

## **Advanced Usage**

### Using Proxies

```python
# SOCKS5 proxy
proxies = {"https": "socks5://user:pass@host:port"}
client = AsyncUltraApiClient(client_kwargs={"proxies": proxies})

# HTTP proxy
proxies = {
    "http": "http://user:pass@proxy.example.com:8080",
    "https": "http://user:pass@proxy.example.com:8080",
}
client = AsyncUltraApiClient(client_kwargs={"proxies": proxies})
```

### Custom DNS Resolution

```python
# Force specific DNS resolution
client = AsyncUltraApiClient(
    client_kwargs={
        "resolve": ["api.jup.ag:443:1.2.3.4"],
        "dns_servers": ["1.1.1.1", "1.0.0.1"],
    }
)
```

### Custom Headers and Browser Impersonation

```python
# Default client
client = AsyncUltraApiClient()

# With custom timeout
client = AsyncUltraApiClient(
    client_kwargs={
        "timeout": 60,  # 60 seconds timeout
    }
)

# With custom headers
client = AsyncUltraApiClient(
    client_kwargs={
        "headers": {
            "Accept-Language": "en-US,en;q=0.9",
        }
    }
)
```

## **Error Handling**

The SDK may raise various exceptions:

### Common Exceptions

```python
try:
    response = await client.order_and_execute(order_request)
except ValueError as e:
    # Invalid private key format
    print(f"Configuration error: {e}")
except requests.HTTPError as e:
    # HTTP errors (4xx, 5xx)
    print(f"API error: {e}")
except Exception as e:
    # Other errors
    print(f"Unexpected error: {e}")
```

### Response Status Handling

```python
response = await client.order_and_execute(order_request)

if response.get("status") == "Failed":
    error_code = response.get("code")
    error_message = response.get("error")

    if error_code == "INSUFFICIENT_BALANCE":
        print("Not enough balance for the swap")
    elif error_code == "SLIPPAGE_EXCEEDED":
        print("Slippage tolerance exceeded")
    else:
        print(f"Transaction failed: {error_message}")
```

## **Contributing**

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to
discuss what you would like to change.

### Development Setup

install [uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) and
[just](https://github.com/casey/just?tab=readme-ov-file#installation)

```bash
# Clone the repository
git clone https://github.com/solanab/pyjupiter.git
cd pyjupiter

# Install development dependencies
uv sync

# Run tests
just ta

# Run linters
just l
just f
```

## **Resources**

- [Ultra API Documentation](https://dev.jup.ag/docs/ultra-api/)
- [Jupiter Portal](https://portal.jup.ag/onboard) - Get your API key
- [Discord Community](https://discord.gg/jup)
- [GitHub Repository](https://github.com/solanab/pyjupiter)

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
