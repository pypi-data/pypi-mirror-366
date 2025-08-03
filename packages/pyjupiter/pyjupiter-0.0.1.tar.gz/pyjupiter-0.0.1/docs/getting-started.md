# Getting Started with Jupiter Python SDK

This guide will help you get up and running with the Jupiter Python SDK in minutes.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.9+** installed on your system
- **A Solana wallet** with some SOL for transaction fees
- **Your wallet's private key** (we'll show you how to set this up securely)

## 🛠️ Installation

### Option 1: Using uv (Recommended)

First, install [uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) if you haven't already:

```bash
# Install pyjupiter
uv add pyjupiter
```

## 🔑 Environment Setup

### 1. Set Your Private Key

You need to set your Solana wallet's private key as an environment variable. The SDK supports two formats:

#### Base58 Format (Recommended)

```bash
# Export your private key (Base58 format)
export PRIVATE_KEY="your_base58_private_key_here"
```

#### Uint8 Array Format

```bash
# Or as a uint8 array
export PRIVATE_KEY="[10,229,131,132,213,96,74,22,...]"
```

### 2. Optional: Get a Jupiter API Key

For enhanced rate limits and features, get an API key from [Jupiter Portal](https://portal.jup.ag/onboard):

```bash
export JUPITER_API_KEY="your_api_key_here"
```

### 3. Create a .env File (Optional)

For development, you can create a `.env` file:

```env
PRIVATE_KEY=your_base58_private_key_here
JUPITER_API_KEY=your_api_key_here
```

## 🚀 Your First Swap

Let's start with a simple token swap example:

### Async Example (Recommended)

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

async def main():
    # Initialize the client
    client = AsyncUltraApiClient()

    print("🔍 Getting wallet address...")
    wallet_address = await client.get_public_key()
    print(f"📍 Wallet: {wallet_address}")

    # Create a swap order: 0.01 WSOL → USDC
    order_request = UltraOrderRequest(
        input_mint="So11111111111111111111111111111111111111112",  # WSOL
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        amount=10000000,  # 0.01 WSOL (in lamports)
        taker=wallet_address,
    )

    try:
        print("🔄 Executing swap...")
        response = await client.order_and_execute(order_request)

        if response.get("status") == "Success":
            signature = response["signature"]
            print(f"✅ Swap successful!")
            print(f"🔗 Transaction: https://solscan.io/tx/{signature}")
        else:
            print(f"❌ Swap failed: {response.get('error')}")

    except Exception as e:
        print(f"💥 Error: {e}")
    finally:
        await client.close()

# Run the async function
asyncio.run(main())
```

### Sync Example

```python
from pyjupiter.clients.ultra_api_client import UltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

# Initialize the sync client
client = UltraApiClient()

print("🔍 Getting wallet address...")
wallet_address = client.get_public_key()
print(f"📍 Wallet: {wallet_address}")

# Create a swap order
order_request = UltraOrderRequest(
    input_mint="So11111111111111111111111111111111111111112",  # WSOL
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    amount=10000000,  # 0.01 WSOL
    taker=wallet_address,
)

try:
    print("🔄 Executing swap...")
    response = client.order_and_execute(order_request)

    if response.get("status") == "Success":
        signature = response["signature"]
        print(f"✅ Swap successful!")
        print(f"🔗 Transaction: https://solscan.io/tx/{signature}")
    else:
        print(f"❌ Swap failed: {response.get('error')}")

except Exception as e:
    print(f"💥 Error: {e}")
finally:
    client.close()
```

## 📊 Check Your Balances

Before making swaps, it's useful to check your token balances:

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

async def check_balances():
    client = AsyncUltraApiClient()

    try:
        # Get your wallet address
        address = await client.get_public_key()
        print(f"📍 Checking balances for: {address}")

        # Fetch balances
        balances = await client.balances(address)

        print("\n💰 Token Balances:")
        print("-" * 40)

        for token, details in balances.items():
            amount = details.get('uiAmount', 0)
            frozen = details.get('isFrozen', False)
            status = "🧊 Frozen" if frozen else "✅ Active"
            print(f"{token:<8} {amount:>12.6f} {status}")

    except Exception as e:
        print(f"💥 Error: {e}")
    finally:
        await client.close()

asyncio.run(check_balances())
```

## 🛡️ Check Token Safety

Always verify token safety before trading:

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

async def check_token_safety():
    client = AsyncUltraApiClient()

    # Tokens to check
    tokens = [
        "So11111111111111111111111111111111111111112",  # WSOL
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
    ]

    try:
        print("🛡️ Checking token safety...")
        shield_response = await client.shield(tokens)

        for mint in tokens:
            warnings = shield_response.get("warnings", {}).get(mint, [])

            if warnings:
                print(f"⚠️  {mint[:8]}... has warnings:")
                for warning in warnings:
                    print(f"   - {warning.get('type')}: {warning.get('message')}")
            else:
                print(f"✅ {mint[:8]}... appears safe")

    except Exception as e:
        print(f"💥 Error: {e}")
    finally:
        await client.close()

asyncio.run(check_token_safety())
```

## ⚙️ Client Configuration

### Basic Configuration

```python
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

# Default configuration
client = AsyncUltraApiClient()

# With API key
client = AsyncUltraApiClient(api_key="your_api_key")

# Custom private key environment variable
client = AsyncUltraApiClient(private_key_env_var="MY_PRIVATE_KEY")
```

### Advanced Configuration

```python
# Custom client settings
client = AsyncUltraApiClient(
    api_key="your_api_key",
    client_kwargs={
        "timeout": 30,  # 30 seconds timeout
        "verify": True,  # SSL verification
        "headers": {
            "User-Agent": "MyApp/1.0",
        }
    }
)
```

### Using Proxies

```python
# SOCKS5 proxy
proxies = {"https": "socks5://user:pass@host:port"}
client = AsyncUltraApiClient(client_kwargs={"proxies": proxies})

# HTTP proxy
proxies = {
    "http": "http://proxy.example.com:8080",
    "https": "http://proxy.example.com:8080",
}
client = AsyncUltraApiClient(client_kwargs={"proxies": proxies})
```

## 🔍 Common Token Addresses

Here are some popular Solana token mint addresses for testing:

| Token       | Symbol | Mint Address                                   | Decimals |
| ----------- | ------ | ---------------------------------------------- | -------- |
| Wrapped SOL | WSOL   | `So11111111111111111111111111111111111111112`  | 9        |
| USD Coin    | USDC   | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | 6        |
| Tether      | USDT   | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` | 6        |
| Bonk        | BONK   | `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263` | 5        |

## 💡 Best Practices

### 1. Always Close Clients

```python
# Using try/finally
client = AsyncUltraApiClient()
try:
    # Your code here
    pass
finally:
    await client.close()

# Or using context manager (if available)
async with AsyncUltraApiClient() as client:
    # Your code here
    pass
```

### 2. Handle Errors Gracefully

```python
try:
    response = await client.order_and_execute(order_request)

    if response.get("status") == "Failed":
        error_code = response.get("code")
        if error_code == "INSUFFICIENT_BALANCE":
            print("❌ Insufficient balance for swap")
        elif error_code == "SLIPPAGE_EXCEEDED":
            print("❌ Slippage tolerance exceeded")
        else:
            print(f"❌ Transaction failed: {response.get('error')}")
    else:
        print(f"✅ Success: {response['signature']}")

except Exception as e:
    print(f"💥 Unexpected error: {e}")
```

### 3. Calculate Amounts Correctly

```python
# Always work with the smallest unit
sol_amount = 0.01  # SOL
lamports = int(sol_amount * 10**9)  # Convert to lamports

usdc_amount = 10.0  # USDC
usdc_units = int(usdc_amount * 10**6)  # USDC has 6 decimals
```

## 🚨 Troubleshooting

### Common Issues

| Problem                                  | Solution                                            |
| ---------------------------------------- | --------------------------------------------------- |
| `ValueError: Invalid private key format` | Check your private key format (Base58 or array)     |
| `ConnectionError`                        | Check your internet connection and proxy settings   |
| `Insufficient balance`                   | Ensure you have enough tokens and SOL for fees      |
| `Slippage exceeded`                      | Market moved too much; try again or adjust slippage |

### Environment Variable Issues

```bash
# Check if your environment variable is set
echo $PRIVATE_KEY

# If empty, set it again
export PRIVATE_KEY="your_private_key_here"
```

### Network Issues

```python
# Test basic connectivity
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

async def test_connection():
    client = AsyncUltraApiClient()
    try:
        address = await client.get_public_key()
        print(f"✅ Connection successful! Wallet: {address}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        await client.close()

asyncio.run(test_connection())
```

## 📚 Next Steps

Now that you have the basics down, explore more advanced features:

1. **[API Reference](api-reference.md)** - Complete method documentation
2. **[Examples](examples.md)** - Real-world use cases and patterns
3. **[Ultra API Docs](https://dev.jup.ag/docs/ultra-api/)** - Official Jupiter documentation

## 🎉 Congratulations!

You've successfully set up Jupiter Python SDK and made your first token swap. You're now ready to build sophisticated
DeFi applications on Solana!
