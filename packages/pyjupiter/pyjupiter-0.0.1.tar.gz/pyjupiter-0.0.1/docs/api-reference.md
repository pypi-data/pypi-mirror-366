# API Reference

Complete reference documentation for the Jupiter Python SDK.

## 📚 Table of Contents

- [Client Classes](#client-classes)
- [Core Methods](#core-methods)
- [Data Models](#data-models)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Utility Methods](#utility-methods)

## 🏛️ Client Classes

### AsyncUltraApiClient

The main asynchronous client for Jupiter Ultra API interactions.

```python
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

client = AsyncUltraApiClient(
    api_key="optional_api_key",
    private_key_env_var="PRIVATE_KEY",
    client_kwargs={}
)
```

**Constructor Parameters:**

| Parameter             | Type          | Default         | Description                               |
| --------------------- | ------------- | --------------- | ----------------------------------------- |
| `api_key`             | `str \| None` | `None`          | Jupiter API key for enhanced features     |
| `private_key_env_var` | `str`         | `"PRIVATE_KEY"` | Environment variable name for private key |
| `client_kwargs`       | `dict`        | `{}`            | Additional curl_cffi client configuration |

### UltraApiClient

The synchronous client for Jupiter Ultra API interactions.

```python
from pyjupiter.clients.ultra_api_client import UltraApiClient

client = UltraApiClient(
    api_key="optional_api_key",
    private_key_env_var="PRIVATE_KEY",
    client_kwargs={}
)
```

**Constructor Parameters:** Same as `AsyncUltraApiClient`

## 🔧 Core Methods

### order()

Create a swap order without executing it.

#### Signature

```python
# Async
async def order(self, request: UltraOrderRequest) -> dict

# Sync
def order(self, request: UltraOrderRequest) -> dict
```

#### Parameters

| Parameter | Type                | Description                 |
| --------- | ------------------- | --------------------------- |
| `request` | `UltraOrderRequest` | Order request configuration |

#### Returns

| Field         | Type  | Description                              |
| ------------- | ----- | ---------------------------------------- |
| `requestId`   | `str` | Unique identifier for the order          |
| `transaction` | `str` | Base64-encoded transaction               |
| `status`      | `str` | Order status (`"Success"` or `"Failed"`) |

#### Example

```python
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

order_request = UltraOrderRequest(
    input_mint="So11111111111111111111111111111111111111112",
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    amount=10000000,
    taker=await client.get_public_key()
)

response = await client.order(order_request)
```

### execute()

Execute a previously created order.

#### Signature

```python
# Async
async def execute(self, request: UltraExecuteRequest) -> dict

# Sync
def execute(self, request: UltraExecuteRequest) -> dict
```

#### Parameters

| Parameter | Type                  | Description                               |
| --------- | --------------------- | ----------------------------------------- |
| `request` | `UltraExecuteRequest` | Execution request with signed transaction |

#### Returns

| Field       | Type  | Description                                  |
| ----------- | ----- | -------------------------------------------- |
| `signature` | `str` | Transaction signature                        |
| `status`    | `str` | Execution status (`"Success"` or `"Failed"`) |
| `error`     | `str` | Error message (if failed)                    |

#### Example

```python
from pyjupiter.models.ultra_api.ultra_execute_request_model import UltraExecuteRequest

execute_request = UltraExecuteRequest(
    request_id=response["requestId"],
    signed_transaction="base64_signed_transaction"
)

result = await client.execute(execute_request)
```

### order_and_execute()

Create and execute an order in a single call.

#### Signature

```python
# Async
async def order_and_execute(self, request: UltraOrderRequest) -> dict

# Sync
def order_and_execute(self, request: UltraOrderRequest) -> dict
```

#### Parameters

| Parameter | Type                | Description                 |
| --------- | ------------------- | --------------------------- |
| `request` | `UltraOrderRequest` | Order request configuration |

#### Returns

Same as `execute()` method.

#### Example

```python
response = await client.order_and_execute(order_request)
print(f"Transaction: https://solscan.io/tx/{response['signature']}")
```

### balances()

Get token balances for a Solana address.

#### Signature

```python
# Async
async def balances(self, address: str) -> dict

# Sync
def balances(self, address: str) -> dict
```

#### Parameters

| Parameter | Type  | Description               |
| --------- | ----- | ------------------------- |
| `address` | `str` | Solana public key address |

#### Returns

Dictionary mapping token symbols to balance details:

| Field      | Type    | Description                         |
| ---------- | ------- | ----------------------------------- |
| `amount`   | `str`   | Raw amount in smallest unit         |
| `uiAmount` | `float` | Human-readable amount               |
| `slot`     | `int`   | Blockchain slot number              |
| `isFrozen` | `bool`  | Whether the token account is frozen |

#### Example

```python
address = await client.get_public_key()
balances = await client.balances(address)

for token, details in balances.items():
    print(f"{token}: {details['uiAmount']} (Frozen: {details['isFrozen']})")
```

### shield()

Check tokens for safety warnings.

#### Signature

```python
# Async
async def shield(self, mints: list[str]) -> dict

# Sync
def shield(self, mints: list[str]) -> dict
```

#### Parameters

| Parameter | Type        | Description                  |
| --------- | ----------- | ---------------------------- |
| `mints`   | `list[str]` | List of token mint addresses |

#### Returns

| Field      | Type   | Description                                |
| ---------- | ------ | ------------------------------------------ |
| `warnings` | `dict` | Mapping of mint addresses to warning lists |

Warning object structure:

| Field     | Type  | Description         |
| --------- | ----- | ------------------- |
| `type`    | `str` | Warning type        |
| `message` | `str` | Warning description |

#### Example

```python
mints = [
    "So11111111111111111111111111111111111111112",  # WSOL
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
]

shield_response = await client.shield(mints)

for mint, warnings in shield_response.get("warnings", {}).items():
    if warnings:
        print(f"⚠️ {mint} has warnings:")
        for warning in warnings:
            print(f"  - {warning['type']}: {warning['message']}")
```

## 📦 Data Models

### UltraOrderRequest

Pydantic model for creating swap orders.

#### Fields

| Field              | Type  | Required | Description                  |
| ------------------ | ----- | -------- | ---------------------------- |
| `input_mint`       | `str` | ✅       | Input token mint address     |
| `output_mint`      | `str` | ✅       | Output token mint address    |
| `amount`           | `int` | ✅       | Amount in smallest unit      |
| `taker`            | `str` | ❌       | Taker's public key           |
| `referral_account` | `str` | ❌       | Referral account address     |
| `referral_fee`     | `int` | ❌       | Referral fee in basis points |

#### Example

```python
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

request = UltraOrderRequest(
    input_mint="So11111111111111111111111111111111111111112",
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    amount=10000000,
    taker="your_public_key",
    referral_account="referral_address",
    referral_fee=50  # 0.5%
)
```

### UltraExecuteRequest

Pydantic model for executing orders.

#### Fields

| Field                | Type  | Required | Description                       |
| -------------------- | ----- | -------- | --------------------------------- |
| `request_id`         | `str` | ✅       | Request ID from order response    |
| `signed_transaction` | `str` | ✅       | Base64-encoded signed transaction |

#### Example

```python
from pyjupiter.models.ultra_api.ultra_execute_request_model import UltraExecuteRequest

request = UltraExecuteRequest(
    request_id="order_request_id",
    signed_transaction="base64_encoded_transaction"
)
```

## ⚙️ Configuration

### Client Configuration

The `client_kwargs` parameter allows extensive customization:

#### Timeout Settings

```python
client = AsyncUltraApiClient(
    client_kwargs={
        "timeout": 30,  # 30 seconds
    }
)
```

#### Proxy Configuration

```python
# SOCKS5 Proxy
client = AsyncUltraApiClient(
    client_kwargs={
        "proxies": {"https": "socks5://user:pass@host:port"}
    }
)

# HTTP Proxy
client = AsyncUltraApiClient(
    client_kwargs={
        "proxies": {
            "http": "http://proxy.example.com:8080",
            "https": "http://proxy.example.com:8080"
        }
    }
)
```

#### Custom Headers

```python
client = AsyncUltraApiClient(
    client_kwargs={
        "headers": {
            "User-Agent": "MyApp/1.0",
            "Accept-Language": "en-US,en;q=0.9"
        }
    }
)
```

#### SSL Configuration

```python
client = AsyncUltraApiClient(
    client_kwargs={
        "verify": True,  # Enable SSL verification
        # or custom CA bundle
        "verify": "/path/to/ca-bundle.crt"
    }
)
```

#### DNS Configuration

```python
client = AsyncUltraApiClient(
    client_kwargs={
        "resolve": ["api.jup.ag:443:1.2.3.4"],
        "dns_servers": ["1.1.1.1", "1.0.0.1"]
    }
)
```

### Environment Variables

| Variable          | Description               | Format                       |
| ----------------- | ------------------------- | ---------------------------- |
| `PRIVATE_KEY`     | Solana wallet private key | Base58 string or uint8 array |
| `JUPITER_API_KEY` | Jupiter API key           | String                       |

#### Private Key Formats

```bash
# Base58 format (recommended)
export PRIVATE_KEY="5KQwr...xyz"

# Uint8 array format
export PRIVATE_KEY="[10,229,131,132,213,96,74,22,...]"
```

## 🚨 Error Handling

### Common Exceptions

| Exception            | Description                 | When It Occurs                                      |
| -------------------- | --------------------------- | --------------------------------------------------- |
| `ValueError`         | Invalid input parameters    | Invalid private key format, missing required fields |
| `requests.HTTPError` | HTTP errors                 | API errors (4xx, 5xx responses)                     |
| `ConnectionError`    | Network connectivity issues | Network problems, proxy issues                      |
| `TimeoutError`       | Request timeout             | Request took too long to complete                   |

### Response Status Codes

| Status      | Description                      |
| ----------- | -------------------------------- |
| `"Success"` | Operation completed successfully |
| `"Failed"`  | Operation failed                 |

### Error Response Structure

Failed responses include additional error information:

| Field    | Type  | Description                          |
| -------- | ----- | ------------------------------------ |
| `status` | `str` | Always `"Failed"`                    |
| `error`  | `str` | Human-readable error message         |
| `code`   | `str` | Error code for programmatic handling |

### Common Error Codes

| Error Code             | Description                  | Possible Solutions           |
| ---------------------- | ---------------------------- | ---------------------------- |
| `INSUFFICIENT_BALANCE` | Not enough tokens for swap   | Check balance, reduce amount |
| `SLIPPAGE_EXCEEDED`    | Price moved beyond tolerance | Retry or adjust slippage     |
| `INVALID_MINT`         | Invalid token mint address   | Verify mint address          |
| `RATE_LIMITED`         | Too many requests            | Add delay between requests   |

### Error Handling Example

```python
try:
    response = await client.order_and_execute(order_request)

    if response.get("status") == "Failed":
        error_code = response.get("code")
        error_message = response.get("error")

        if error_code == "INSUFFICIENT_BALANCE":
            print("❌ Insufficient balance for swap")
        elif error_code == "SLIPPAGE_EXCEEDED":
            print("❌ Price moved too much, try again")
        else:
            print(f"❌ Error: {error_message}")
    else:
        print(f"✅ Success: {response['signature']}")

except ValueError as e:
    print(f"❌ Configuration error: {e}")
except requests.HTTPError as e:
    print(f"❌ API error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

## 🛠️ Utility Methods

### get_public_key()

Get the public key of the configured wallet.

#### Signature

```python
# Async
async def get_public_key(self) -> str

# Sync
def get_public_key(self) -> str
```

#### Returns

| Type  | Description               |
| ----- | ------------------------- |
| `str` | Base58-encoded public key |

#### Example

```python
public_key = await client.get_public_key()
print(f"Wallet address: {public_key}")
```

### close()

Close the client and clean up resources.

#### Signature

```python
# Async
async def close(self) -> None

# Sync
def close(self) -> None
```

#### Example

```python
# Always close clients when done
try:
    # Your operations here
    pass
finally:
    await client.close()  # For async client
    # client.close()      # For sync client
```

## 🔍 Advanced Usage Patterns

### Rate Limiting

```python
import asyncio

# Semaphore for concurrent request limiting
semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests

async def rate_limited_request(client, mint):
    async with semaphore:
        return await client.shield([mint])
```

### Retry Logic

```python
import asyncio

async def retry_operation(operation, max_retries=3, delay=1.0):
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(delay * (attempt + 1))
```

### Batch Operations

```python
async def batch_shield_check(client, mint_lists):
    tasks = [client.shield(mints) for mints in mint_lists]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Context Manager Pattern

```python
class ManagedClient:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.client = None

    async def __aenter__(self):
        self.client = AsyncUltraApiClient(**self.kwargs)
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.close()

# Usage
async with ManagedClient(api_key="your_key") as client:
    response = await client.balances(address)
```

## 📊 Performance Tips

### Connection Reuse

```python
# Good: Reuse client for multiple operations
client = AsyncUltraApiClient()
try:
    for address in addresses:
        balances = await client.balances(address)
        # Process balances
finally:
    await client.close()

# Avoid: Creating new client for each operation
for address in addresses:
    client = AsyncUltraApiClient()
    balances = await client.balances(address)
    await client.close()  # Inefficient
```

### Concurrent Operations

```python
# Efficient concurrent processing
async def process_addresses(client, addresses):
    tasks = [client.balances(addr) for addr in addresses]
    results = await asyncio.gather(*tasks)
    return results
```

### Timeout Configuration

```python
# Set appropriate timeouts for your use case
client = AsyncUltraApiClient(
    client_kwargs={
        "timeout": 10,  # Quick operations
        # "timeout": 60,  # For slower operations
    }
)
```

---

For more examples and use cases, see the [Examples](examples.md) documentation.
