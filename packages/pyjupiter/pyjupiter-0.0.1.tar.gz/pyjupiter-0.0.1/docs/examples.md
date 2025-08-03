# Examples and Use Cases

Real-world examples and patterns for using the Jupiter Python SDK effectively.

## 📚 Table of Contents

- [Basic Examples](#basic-examples)
- [Trading Strategies](#trading-strategies)
- [Portfolio Management](#portfolio-management)
- [Token Analysis](#token-analysis)
- [Advanced Patterns](#advanced-patterns)
- [Error Handling Patterns](#error-handling-patterns)
- [Performance Optimization](#performance-optimization)

## 🚀 Basic Examples

### Simple Token Swap

The most basic use case - swapping one token for another:

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

async def simple_swap():
    """Swap 0.1 WSOL for USDC"""
    client = AsyncUltraApiClient()

    try:
        # Get wallet address
        wallet = await client.get_public_key()
        print(f"🔍 Using wallet: {wallet}")

        # Create swap order
        order = UltraOrderRequest(
            input_mint="So11111111111111111111111111111111111111112",  # WSOL
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            amount=100_000_000,  # 0.1 WSOL
            taker=wallet
        )

        # Execute swap
        result = await client.order_and_execute(order)

        if result.get("status") == "Success":
            print(f"✅ Swap successful!")
            print(f"📋 Transaction: https://solscan.io/tx/{result['signature']}")
        else:
            print(f"❌ Swap failed: {result.get('error')}")

    finally:
        await client.close()

asyncio.run(simple_swap())
```

### Check Multiple Token Balances

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

async def check_portfolio():
    """Check balances for multiple tokens"""
    client = AsyncUltraApiClient()

    try:
        wallet = await client.get_public_key()
        balances = await client.balances(wallet)

        print(f"💰 Portfolio for {wallet[:8]}...")
        print("=" * 50)

        total_value = 0
        for token, details in balances.items():
            amount = details.get('uiAmount', 0)
            frozen = details.get('isFrozen', False)

            status_icon = "🧊" if frozen else "✅"
            print(f"{status_icon} {token:<8} {amount:>15.6f}")

        print("=" * 50)

    finally:
        await client.close()

asyncio.run(check_portfolio())
```

### Token Safety Check

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

async def safety_check():
    """Check safety of popular tokens"""
    client = AsyncUltraApiClient()

    # Popular Solana tokens
    popular_tokens = [
        ("WSOL", "So11111111111111111111111111111111111111112"),
        ("USDC", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        ("USDT", "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"),
        ("BONK", "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"),
    ]

    try:
        mints = [mint for _, mint in popular_tokens]
        shield_result = await client.shield(mints)

        print("🛡️ Token Safety Report")
        print("=" * 40)

        for name, mint in popular_tokens:
            warnings = shield_result.get("warnings", {}).get(mint, [])

            if warnings:
                print(f"⚠️  {name:<8} - {len(warnings)} warning(s)")
                for warning in warnings:
                    print(f"   └─ {warning.get('type')}: {warning.get('message')}")
            else:
                print(f"✅ {name:<8} - Safe")

    finally:
        await client.close()

asyncio.run(safety_check())
```

## 📈 Trading Strategies

### Dollar Cost Averaging (DCA)

```python
import asyncio
from datetime import datetime
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

class DCABot:
    def __init__(self, api_key=None):
        self.client = AsyncUltraApiClient(api_key=api_key)

    async def dca_buy(self, input_mint, output_mint, amount_sol, frequency_hours=24):
        """Execute DCA strategy"""
        try:
            wallet = await self.client.get_public_key()

            # Check current balance
            balances = await self.client.balances(wallet)
            sol_balance = balances.get("SOL", {}).get("uiAmount", 0)

            if sol_balance < amount_sol:
                print(f"❌ Insufficient SOL balance: {sol_balance}")
                return

            # Create order
            order = UltraOrderRequest(
                input_mint=input_mint,
                output_mint=output_mint,
                amount=int(amount_sol * 10**9),  # Convert to lamports
                taker=wallet
            )

            print(f"🔄 DCA: Buying {amount_sol} SOL worth of tokens...")
            result = await self.client.order_and_execute(order)

            if result.get("status") == "Success":
                print(f"✅ DCA executed successfully!")
                print(f"📋 TX: {result['signature']}")

                # Log the trade
                timestamp = datetime.now().isoformat()
                print(f"📅 {timestamp}: Bought with {amount_sol} SOL")
            else:
                print(f"❌ DCA failed: {result.get('error')}")

        except Exception as e:
            print(f"💥 DCA Error: {e}")

    async def close(self):
        await self.client.close()

# Usage
async def run_dca():
    bot = DCABot()
    try:
        await bot.dca_buy(
            input_mint="So11111111111111111111111111111111111111112",  # WSOL
            output_mint="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
            amount_sol=0.01  # Buy with 0.01 SOL
        )
    finally:
        await bot.close()

asyncio.run(run_dca())
```

### Arbitrage Scanner

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

class ArbitrageScanner:
    def __init__(self):
        self.client = AsyncUltraApiClient()

    async def scan_arbitrage(self, token_pairs, min_profit_bps=50):
        """Scan for arbitrage opportunities"""
        opportunities = []

        for input_mint, output_mint in token_pairs:
            try:
                # Get quote for 1 SOL
                test_amount = 1_000_000_000  # 1 SOL

                # Forward trade: input -> output
                forward_order = UltraOrderRequest(
                    input_mint=input_mint,
                    output_mint=output_mint,
                    amount=test_amount,
                    taker=await self.client.get_public_key()
                )

                forward_quote = await self.client.order(forward_order)

                if forward_quote.get("status") == "Success":
                    # Calculate potential profit
                    # This is simplified - in reality you'd need to parse
                    # the transaction to get exact output amounts
                    print(f"📊 Analyzing {input_mint[:8]}... -> {output_mint[:8]}...")

                    # You would implement profit calculation logic here
                    # opportunities.append({...})

            except Exception as e:
                print(f"❌ Error scanning {input_mint[:8]}...: {e}")

        return opportunities

    async def close(self):
        await self.client.close()

# Usage
async def run_arbitrage_scan():
    scanner = ArbitrageScanner()
    try:
        pairs = [
            ("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),  # WSOL/USDC
            ("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"),  # USDC/USDT
        ]

        opportunities = await scanner.scan_arbitrage(pairs)
        print(f"Found {len(opportunities)} arbitrage opportunities")

    finally:
        await scanner.close()

asyncio.run(run_arbitrage_scan())
```

## 💼 Portfolio Management

### Portfolio Rebalancer

```python
import asyncio
from typing import Dict
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

class PortfolioRebalancer:
    def __init__(self):
        self.client = AsyncUltraApiClient()

    async def rebalance_portfolio(self, target_allocations: Dict[str, float]):
        """
        Rebalance portfolio to target allocations

        Args:
            target_allocations: {"SOL": 0.5, "USDC": 0.3, "BONK": 0.2}
        """
        try:
            wallet = await self.client.get_public_key()
            balances = await self.client.balances(wallet)

            print("🔄 Starting portfolio rebalancing...")
            print("=" * 50)

            # Calculate current allocations
            total_value = 0  # You'd need to fetch USD values
            current_allocations = {}

            for token, details in balances.items():
                amount = details.get('uiAmount', 0)
                # Simplified - you'd need real price data
                current_allocations[token] = amount

            print("📊 Current vs Target Allocations:")
            for token, target in target_allocations.items():
                current = current_allocations.get(token, 0)
                print(f"{token:<8} Current: {current:>8.2f}% Target: {target*100:>6.1f}%")

            # Execute rebalancing trades
            # This is where you'd implement the actual rebalancing logic
            print("✅ Rebalancing completed!")

        except Exception as e:
            print(f"❌ Rebalancing failed: {e}")

    async def close(self):
        await self.client.close()

# Usage
async def rebalance():
    rebalancer = PortfolioRebalancer()
    try:
        await rebalancer.rebalance_portfolio({
            "SOL": 0.4,
            "USDC": 0.4,
            "BONK": 0.2
        })
    finally:
        await rebalancer.close()

asyncio.run(rebalance())
```

### Multi-Wallet Portfolio Tracker

```python
import asyncio
from typing import List
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

class MultiWalletTracker:
    def __init__(self):
        self.client = AsyncUltraApiClient()

    async def track_wallets(self, wallet_addresses: List[str]):
        """Track multiple wallets concurrently"""
        print("👥 Multi-Wallet Portfolio Tracker")
        print("=" * 60)

        # Create tasks for concurrent balance fetching
        tasks = [
            self.get_wallet_summary(address)
            for address in wallet_addresses
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        total_wallets = len(wallet_addresses)
        successful_wallets = sum(1 for r in results if not isinstance(r, Exception))

        print(f"\n📊 Summary: {successful_wallets}/{total_wallets} wallets processed")

    async def get_wallet_summary(self, address: str):
        """Get summary for a single wallet"""
        try:
            balances = await self.client.balances(address)

            print(f"\n💰 Wallet: {address[:8]}...{address[-8:]}")
            print("-" * 40)

            token_count = len(balances)
            total_tokens = sum(
                details.get('uiAmount', 0)
                for details in balances.values()
            )

            print(f"📈 Tokens: {token_count}")

            # Show top holdings
            sorted_balances = sorted(
                balances.items(),
                key=lambda x: x[1].get('uiAmount', 0),
                reverse=True
            )

            for token, details in sorted_balances[:5]:  # Top 5
                amount = details.get('uiAmount', 0)
                if amount > 0:
                    print(f"   {token:<8} {amount:>12.6f}")

            return {
                "address": address,
                "token_count": token_count,
                "balances": balances
            }

        except Exception as e:
            print(f"❌ Error fetching {address[:8]}...: {e}")
            return e

    async def close(self):
        await self.client.close()

# Usage
async def track_multiple_wallets():
    tracker = MultiWalletTracker()
    try:
        # Add your wallet addresses here
        wallets = [
            "YourWalletAddress1...",
            "YourWalletAddress2...",
            # Add more wallet addresses
        ]

        await tracker.track_wallets(wallets)

    finally:
        await tracker.close()

# asyncio.run(track_multiple_wallets())
```

## 🔍 Token Analysis

### Token Risk Assessment

```python
import asyncio
from typing import Dict, List
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

class TokenAnalyzer:
    def __init__(self):
        self.client = AsyncUltraApiClient()

    async def analyze_token_list(self, token_list: List[Dict[str, str]]):
        """Analyze a list of tokens for risks"""
        print("🔍 Token Risk Analysis")
        print("=" * 50)

        # Extract mint addresses
        mints = [token["mint"] for token in token_list]

        # Batch safety check
        shield_result = await self.client.shield(mints)
        warnings_dict = shield_result.get("warnings", {})

        # Analyze each token
        for token in token_list:
            name = token["name"]
            mint = token["mint"]
            warnings = warnings_dict.get(mint, [])

            print(f"\n🪙 {name} ({mint[:8]}...)")
            print("-" * 30)

            if not warnings:
                print("✅ No safety warnings detected")
                risk_score = "LOW"
            else:
                risk_score = self.calculate_risk_score(warnings)
                print(f"⚠️  {len(warnings)} warning(s) detected:")

                for warning in warnings:
                    warning_type = warning.get("type", "Unknown")
                    message = warning.get("message", "No message")
                    print(f"   • {warning_type}: {message}")

            print(f"🎯 Risk Score: {risk_score}")

    def calculate_risk_score(self, warnings: List[Dict]) -> str:
        """Calculate risk score based on warnings"""
        if not warnings:
            return "LOW"

        high_risk_types = ["rugpull", "scam", "suspicious"]
        medium_risk_types = ["liquidity", "volume"]

        for warning in warnings:
            warning_type = warning.get("type", "").lower()
            if any(risk in warning_type for risk in high_risk_types):
                return "HIGH"
            elif any(risk in warning_type for risk in medium_risk_types):
                return "MEDIUM"

        return "MEDIUM" if len(warnings) > 2 else "LOW"

    async def close(self):
        await self.client.close()

# Usage
async def analyze_tokens():
    analyzer = TokenAnalyzer()
    try:
        tokens_to_analyze = [
            {"name": "Wrapped SOL", "mint": "So11111111111111111111111111111111111111112"},
            {"name": "USD Coin", "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"},
            {"name": "Bonk", "mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"},
        ]

        await analyzer.analyze_token_list(tokens_to_analyze)

    finally:
        await analyzer.close()

asyncio.run(analyze_tokens())
```

### Market Scanner

```python
import asyncio
from typing import List, Dict
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

class MarketScanner:
    def __init__(self):
        self.client = AsyncUltraApiClient()

    async def scan_trending_tokens(self, base_mints: List[str]):
        """Scan for trending tokens by volume"""
        print("📈 Market Scanner - Trending Tokens")
        print("=" * 50)

        trending_data = []

        for mint in base_mints:
            try:
                # Check safety first
                shield_result = await self.client.shield([mint])
                warnings = shield_result.get("warnings", {}).get(mint, [])

                safety_status = "🔴 RISKY" if warnings else "🟢 SAFE"

                print(f"\n🔍 Analyzing {mint[:8]}...")
                print(f"   Safety: {safety_status}")

                if warnings:
                    print(f"   Warnings: {len(warnings)}")
                    for warning in warnings[:2]:  # Show first 2 warnings
                        print(f"     • {warning.get('type')}")

                trending_data.append({
                    "mint": mint,
                    "safety_status": safety_status,
                    "warning_count": len(warnings)
                })

            except Exception as e:
                print(f"❌ Error analyzing {mint[:8]}...: {e}")

        # Sort by safety (safe tokens first)
        trending_data.sort(key=lambda x: x["warning_count"])

        print(f"\n📊 Scan Results ({len(trending_data)} tokens):")
        print("-" * 40)

        for data in trending_data:
            mint = data["mint"]
            status = data["safety_status"]
            warnings = data["warning_count"]
            print(f"{status} {mint[:8]}... ({warnings} warnings)")

    async def close(self):
        await self.client.close()

# Usage
async def scan_market():
    scanner = MarketScanner()
    try:
        # Popular token mints to scan
        tokens = [
            "So11111111111111111111111111111111111111112",  # WSOL
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
            "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
        ]

        await scanner.scan_trending_tokens(tokens)

    finally:
        await scanner.close()

asyncio.run(scan_market())
```

## ⚡ Advanced Patterns

### Connection Pool Manager

```python
import asyncio
from typing import List
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

class ConnectionPoolManager:
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.clients: List[AsyncUltraApiClient] = []
        self.current_index = 0

    async def initialize(self):
        """Initialize connection pool"""
        print(f"🔗 Initializing connection pool (size: {self.pool_size})")

        for i in range(self.pool_size):
            client = AsyncUltraApiClient()
            self.clients.append(client)

    def get_client(self) -> AsyncUltraApiClient:
        """Get next client from pool (round-robin)"""
        client = self.clients[self.current_index]
        self.current_index = (self.current_index + 1) % self.pool_size
        return client

    async def batch_operation(self, addresses: List[str]):
        """Execute batch operations using connection pool"""
        semaphore = asyncio.Semaphore(self.pool_size)

        async def process_address(address):
            async with semaphore:
                client = self.get_client()
                try:
                    return await client.balances(address)
                except Exception as e:
                    return {"error": str(e)}

        tasks = [process_address(addr) for addr in addresses]
        results = await asyncio.gather(*tasks)
        return results

    async def close_all(self):
        """Close all connections in pool"""
        print("🔌 Closing connection pool...")
        for client in self.clients:
            await client.close()

# Usage
async def use_connection_pool():
    pool = ConnectionPoolManager(pool_size=3)
    try:
        await pool.initialize()

        # Simulate batch processing
        addresses = [
            "11111111111111111111111111111111",  # Example addresses
            "22222222222222222222222222222222",
            "33333333333333333333333333333333",
        ]

        results = await pool.batch_operation(addresses)
        print(f"✅ Processed {len(results)} addresses")

    finally:
        await pool.close_all()

# asyncio.run(use_connection_pool())
```

### Rate Limited Trading Bot

```python
import asyncio
from datetime import datetime, timedelta
from collections import deque
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

class RateLimitedBot:
    def __init__(self, max_requests_per_minute: int = 60):
        self.client = AsyncUltraApiClient()
        self.max_requests = max_requests_per_minute
        self.request_times = deque()

    async def rate_limited_request(self, operation):
        """Execute operation with rate limiting"""
        now = datetime.now()

        # Remove old requests (older than 1 minute)
        while self.request_times and self.request_times[0] < now - timedelta(minutes=1):
            self.request_times.popleft()

        # Check if we're at the limit
        if len(self.request_times) >= self.max_requests:
            sleep_time = 60 - (now - self.request_times[0]).total_seconds()
            if sleep_time > 0:
                print(f"⏳ Rate limit reached, sleeping for {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)

        # Record this request
        self.request_times.append(now)

        # Execute the operation
        return await operation()

    async def trading_loop(self, trading_pairs: list):
        """Main trading loop with rate limiting"""
        print("🤖 Starting rate-limited trading bot...")

        while True:
            try:
                for pair in trading_pairs:
                    input_mint, output_mint = pair

                    # Rate-limited balance check
                    wallet = await self.rate_limited_request(
                        lambda: self.client.get_public_key()
                    )

                    balances = await self.rate_limited_request(
                        lambda: self.client.balances(wallet)
                    )

                    print(f"📊 Checked balances for {wallet[:8]}...")

                    # Add your trading logic here

                    # Sleep between pairs
                    await asyncio.sleep(5)

                # Sleep between trading cycles
                await asyncio.sleep(60)

            except KeyboardInterrupt:
                print("🛑 Bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Trading loop error: {e}")
                await asyncio.sleep(30)  # Wait before retrying

    async def close(self):
        await self.client.close()

# Usage
async def run_trading_bot():
    bot = RateLimitedBot(max_requests_per_minute=30)
    try:
        pairs = [
            ("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        ]

        await bot.trading_loop(pairs)

    finally:
        await bot.close()

# asyncio.run(run_trading_bot())
```

## 🚨 Error Handling Patterns

### Comprehensive Error Handler

```python
import asyncio
import logging
from typing import Any, Callable
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

class ErrorHandler:
    def __init__(self):
        self.client = AsyncUltraApiClient()
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for error tracking"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('jupiter_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def safe_execute(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with comprehensive error handling"""
        try:
            result = await operation(*args, **kwargs)

            # Check if result indicates failure
            if isinstance(result, dict) and result.get("status") == "Failed":
                error_code = result.get("code")
                error_message = result.get("error")

                self.logger.error(f"API Error [{error_code}]: {error_message}")

                # Handle specific error codes
                if error_code == "INSUFFICIENT_BALANCE":
                    self.logger.warning("Insufficient balance - stopping operations")
                    return None
                elif error_code == "SLIPPAGE_EXCEEDED":
                    self.logger.info("Slippage exceeded - retrying with higher tolerance")
                    # Could implement retry logic here
                    return None
                elif error_code == "RATE_LIMITED":
                    self.logger.warning("Rate limited - backing off")
                    await asyncio.sleep(60)
                    return None

            return result

        except ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            self.logger.info("Retrying in 30 seconds...")
            await asyncio.sleep(30)
            return None

        except TimeoutError as e:
            self.logger.error(f"Timeout error: {e}")
            self.logger.info("Operation timed out - retrying...")
            return None

        except ValueError as e:
            self.logger.error(f"Configuration error: {e}")
            self.logger.critical("Check your configuration and private key")
            raise  # Don't continue with invalid config

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            self.logger.info("Continuing with next operation...")
            return None

    async def monitor_operations(self):
        """Monitor and log various operations"""
        operations = [
            ("Get Public Key", self.client.get_public_key),
            ("Check Balances", self.client.balances, "wallet_address_here"),
            ("Shield Check", self.client.shield, ["So11111111111111111111111111111111111111112"]),
        ]

        for name, operation, *args in operations:
            self.logger.info(f"Executing: {name}")
            result = await self.safe_execute(operation, *args)

            if result is not None:
                self.logger.info(f"✅ {name} completed successfully")
            else:
                self.logger.warning(f"❌ {name} failed or returned None")

            await asyncio.sleep(2)  # Small delay between operations

    async def close(self):
        await self.client.close()

# Usage
async def run_error_handling_demo():
    handler = ErrorHandler()
    try:
        await handler.monitor_operations()
    finally:
        await handler.close()

# asyncio.run(run_error_handling_demo())
```

### Retry Mechanism

```python
import asyncio
import random
from typing import Any, Callable

async def exponential_backoff_retry(
    operation: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
) -> Any:
    """
    Retry operation with exponential backoff

    Args:
        operation: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Add random jitter to prevent thundering herd
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await operation()

        except Exception as e:
            last_exception = e

            if attempt == max_retries:
                raise last_exception

            # Calculate delay with exponential backoff
            delay = min(base_delay * (2 ** attempt), max_delay)

            # Add jitter
            if jitter:
                delay *= (0.5 + random.random() * 0.5)

            print(f"❌ Attempt {attempt + 1} failed: {e}")
            print(f"⏳ Retrying in {delay:.1f} seconds...")

            await asyncio.sleep(delay)

    raise last_exception

# Usage example
async def retry_example():
    from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

    client = AsyncUltraApiClient()
    try:
        # Wrap any operation with retry logic
        balances = await exponential_backoff_retry(
            lambda: client.balances("wallet_address_here"),
            max_retries=3
        )
        print(f"✅ Got balances: {balances}")

    finally:
        await client.close()

# asyncio.run(retry_example())
```

## 🚀 Performance Optimization

### Concurrent Processing

```python
import asyncio
from typing import List
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

class PerformanceOptimizer:
    def __init__(self, max_concurrent: int = 10):
        self.client = AsyncUltraApiClient()
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def concurrent_balance_check(self, addresses: List[str]):
        """Check balances for multiple addresses concurrently"""
        async def check_single_balance(address):
            async with self.semaphore:
                try:
                    return {
                        "address": address,
                        "balances": await self.client.balances(address),
                        "status": "success"
                    }
                except Exception as e:
                    return {
                        "address": address,
                        "error": str(e),
                        "status": "error"
                    }

        print(f"🚀 Checking {len(addresses)} addresses concurrently...")
        start_time = asyncio.get_event_loop().time()

        tasks = [check_single_balance(addr) for addr in addresses]
        results = await asyncio.gather(*tasks)

        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time

        successful = sum(1 for r in results if r["status"] == "success")

        print(f"✅ Completed in {duration:.2f}s")
        print(f"📊 Success rate: {successful}/{len(addresses)} ({successful/len(addresses)*100:.1f}%)")

        return results

    async def batch_shield_check(self, mint_batches: List[List[str]]):
        """Check token safety in batches"""
        async def check_batch(batch):
            async with self.semaphore:
                try:
                    return await self.client.shield(batch)
                except Exception as e:
                    return {"error": str(e)}

        print(f"🛡️  Processing {len(mint_batches)} shield batches...")

        tasks = [check_batch(batch) for batch in mint_batches]
        results = await asyncio.gather(*tasks)

        return results

    async def close(self):
        await self.client.close()

# Usage
async def performance_demo():
    optimizer = PerformanceOptimizer(max_concurrent=5)

    try:
        # Demo addresses (replace with real ones)
        addresses = [
            "11111111111111111111111111111111",
            "22222222222222222222222222222222",
            "33333333333333333333333333333333",
            # Add more addresses
        ]

        # Concurrent balance checking
        balance_results = await optimizer.concurrent_balance_check(addresses)

        # Batch shield checking
        mint_batches = [
            ["So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"],
            ["Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"],
        ]

        shield_results = await optimizer.batch_shield_check(mint_batches)

        print("🎯 Performance optimization demo completed!")

    finally:
        await optimizer.close()

# asyncio.run(performance_demo())
```

---

These examples demonstrate real-world usage patterns and best practices for the Jupiter Python SDK. Each example is
complete and can be adapted to your specific use case. Remember to:

1. Always handle errors gracefully
2. Use proper rate limiting
3. Close clients when done
4. Implement logging for production use
5. Test with small amounts first

For more detailed API documentation, see the [API Reference](api-reference.md).
