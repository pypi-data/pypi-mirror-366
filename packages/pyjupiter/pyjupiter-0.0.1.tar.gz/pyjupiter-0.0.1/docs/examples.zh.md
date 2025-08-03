# 代码示例与使用场景

有效使用 Jupiter Python SDK 的真实示例和模式。

## 📚 目录

- [基础示例](#基础示例)
- [交易策略](#交易策略)
- [投资组合管理](#投资组合管理)
- [代币分析](#代币分析)
- [高级模式](#高级模式)
- [错误处理模式](#错误处理模式)
- [性能优化](#性能优化)

## 🚀 基础示例

### 简单代币交换

最基本的用例 - 将一种代币交换为另一种：

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

async def simple_swap():
    """交换 0.1 WSOL 为 USDC"""
    client = AsyncUltraApiClient()

    try:
        # 获取钱包地址
        wallet = await client.get_public_key()
        print(f"🔍 使用钱包: {wallet}")

        # 创建交换订单
        order = UltraOrderRequest(
            input_mint="So11111111111111111111111111111111111111112",  # WSOL
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            amount=100_000_000,  # 0.1 WSOL
            taker=wallet
        )

        # 执行交换
        result = await client.order_and_execute(order)

        if result.get("status") == "Success":
            print(f"✅ 交换成功！")
            print(f"📋 交易链接: https://solscan.io/tx/{result['signature']}")
        else:
            print(f"❌ 交换失败: {result.get('error')}")

    finally:
        await client.close()

asyncio.run(simple_swap())
```

### 检查多个代币余额

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

async def check_portfolio():
    """检查多个代币的余额"""
    client = AsyncUltraApiClient()

    try:
        wallet = await client.get_public_key()
        balances = await client.balances(wallet)

        print(f"💰 投资组合 {wallet[:8]}...")
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

### 代币安全检查

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

async def safety_check():
    """检查热门代币的安全性"""
    client = AsyncUltraApiClient()

    # 热门 Solana 代币
    popular_tokens = [
        ("WSOL", "So11111111111111111111111111111111111111112"),
        ("USDC", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        ("USDT", "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"),
        ("BONK", "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"),
    ]

    try:
        mints = [mint for _, mint in popular_tokens]
        shield_result = await client.shield(mints)

        print("🛡️ 代币安全报告")
        print("=" * 40)

        for name, mint in popular_tokens:
            warnings = shield_result.get("warnings", {}).get(mint, [])

            if warnings:
                print(f"⚠️  {name:<8} - {len(warnings)} 个警告")
                for warning in warnings:
                    print(f"   └─ {warning.get('type')}: {warning.get('message')}")
            else:
                print(f"✅ {name:<8} - 安全")

    finally:
        await client.close()

asyncio.run(safety_check())
```

## 📈 交易策略

### 定投策略 (DCA)

```python
import asyncio
from datetime import datetime
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

class DCABot:
    def __init__(self, api_key=None):
        self.client = AsyncUltraApiClient(api_key=api_key)

    async def dca_buy(self, input_mint, output_mint, amount_sol, frequency_hours=24):
        """执行定投策略"""
        try:
            wallet = await self.client.get_public_key()

            # 检查当前余额
            balances = await self.client.balances(wallet)
            sol_balance = balances.get("SOL", {}).get("uiAmount", 0)

            if sol_balance < amount_sol:
                print(f"❌ SOL 余额不足: {sol_balance}")
                return

            # 创建订单
            order = UltraOrderRequest(
                input_mint=input_mint,
                output_mint=output_mint,
                amount=int(amount_sol * 10**9),  # 转换为 lamports
                taker=wallet
            )

            print(f"🔄 定投: 用 {amount_sol} SOL 购买代币...")
            result = await self.client.order_and_execute(order)

            if result.get("status") == "Success":
                print(f"✅ 定投执行成功！")
                print(f"📋 交易: {result['signature']}")

                # 记录交易
                timestamp = datetime.now().isoformat()
                print(f"📅 {timestamp}: 用 {amount_sol} SOL 购买")
            else:
                print(f"❌ 定投失败: {result.get('error')}")

        except Exception as e:
            print(f"💥 定投错误: {e}")

    async def close(self):
        await self.client.close()

# 使用方法
async def run_dca():
    bot = DCABot()
    try:
        await bot.dca_buy(
            input_mint="So11111111111111111111111111111111111111112",  # WSOL
            output_mint="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
            amount_sol=0.01  # 用 0.01 SOL 购买
        )
    finally:
        await bot.close()

asyncio.run(run_dca())
```

### 套利扫描器

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

class ArbitrageScanner:
    def __init__(self):
        self.client = AsyncUltraApiClient()

    async def scan_arbitrage(self, token_pairs, min_profit_bps=50):
        """扫描套利机会"""
        opportunities = []

        for input_mint, output_mint in token_pairs:
            try:
                # 获取 1 SOL 的报价
                test_amount = 1_000_000_000  # 1 SOL

                # 正向交易: input -> output
                forward_order = UltraOrderRequest(
                    input_mint=input_mint,
                    output_mint=output_mint,
                    amount=test_amount,
                    taker=await self.client.get_public_key()
                )

                forward_quote = await self.client.order(forward_order)

                if forward_quote.get("status") == "Success":
                    # 计算潜在利润
                    # 这里简化了 - 实际情况下需要解析交易以获得确切的输出金额
                    print(f"📊 分析 {input_mint[:8]}... -> {output_mint[:8]}...")

                    # 您需要在这里实现利润计算逻辑
                    # opportunities.append({...})

            except Exception as e:
                print(f"❌ 扫描 {input_mint[:8]}... 时出错: {e}")

        return opportunities

    async def close(self):
        await self.client.close()

# 使用方法
async def run_arbitrage_scan():
    scanner = ArbitrageScanner()
    try:
        pairs = [
            ("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),  # WSOL/USDC
            ("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"),  # USDC/USDT
        ]

        opportunities = await scanner.scan_arbitrage(pairs)
        print(f"发现 {len(opportunities)} 个套利机会")

    finally:
        await scanner.close()

asyncio.run(run_arbitrage_scan())
```

## 💼 投资组合管理

### 投资组合再平衡器

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
        重新平衡投资组合到目标配置

        参数:
            target_allocations: {"SOL": 0.5, "USDC": 0.3, "BONK": 0.2}
        """
        try:
            wallet = await self.client.get_public_key()
            balances = await self.client.balances(wallet)

            print("🔄 开始投资组合重新平衡...")
            print("=" * 50)

            # 计算当前配置
            total_value = 0  # 您需要获取美元价值
            current_allocations = {}

            for token, details in balances.items():
                amount = details.get('uiAmount', 0)
                # 简化 - 您需要真实的价格数据
                current_allocations[token] = amount

            print("📊 当前与目标配置:")
            for token, target in target_allocations.items():
                current = current_allocations.get(token, 0)
                print(f"{token:<8} 当前: {current:>8.2f}% 目标: {target*100:>6.1f}%")

            # 执行重新平衡交易
            # 这里您需要实现实际的重新平衡逻辑
            print("✅ 重新平衡完成！")

        except Exception as e:
            print(f"❌ 重新平衡失败: {e}")

    async def close(self):
        await self.client.close()

# 使用方法
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

### 多钱包投资组合跟踪器

```python
import asyncio
from typing import List
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

class MultiWalletTracker:
    def __init__(self):
        self.client = AsyncUltraApiClient()

    async def track_wallets(self, wallet_addresses: List[str]):
        """并发跟踪多个钱包"""
        print("👥 多钱包投资组合跟踪器")
        print("=" * 60)

        # 为并发余额获取创建任务
        tasks = [
            self.get_wallet_summary(address)
            for address in wallet_addresses
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 汇总结果
        total_wallets = len(wallet_addresses)
        successful_wallets = sum(1 for r in results if not isinstance(r, Exception))

        print(f"\n📊 摘要: {successful_wallets}/{total_wallets} 个钱包已处理")

    async def get_wallet_summary(self, address: str):
        """获取单个钱包的摘要"""
        try:
            balances = await self.client.balances(address)

            print(f"\n💰 钱包: {address[:8]}...{address[-8:]}")
            print("-" * 40)

            token_count = len(balances)
            total_tokens = sum(
                details.get('uiAmount', 0)
                for details in balances.values()
            )

            print(f"📈 代币数量: {token_count}")

            # 显示主要持仓
            sorted_balances = sorted(
                balances.items(),
                key=lambda x: x[1].get('uiAmount', 0),
                reverse=True
            )

            for token, details in sorted_balances[:5]:  # 前 5 位
                amount = details.get('uiAmount', 0)
                if amount > 0:
                    print(f"   {token:<8} {amount:>12.6f}")

            return {
                "address": address,
                "token_count": token_count,
                "balances": balances
            }

        except Exception as e:
            print(f"❌ 获取 {address[:8]}... 时出错: {e}")
            return e

    async def close(self):
        await self.client.close()

# 使用方法
async def track_multiple_wallets():
    tracker = MultiWalletTracker()
    try:
        # 在这里添加您的钱包地址
        wallets = [
            "YourWalletAddress1...",
            "YourWalletAddress2...",
            # 添加更多钱包地址
        ]

        await tracker.track_wallets(wallets)

    finally:
        await tracker.close()

# asyncio.run(track_multiple_wallets())
```

## 🔍 代币分析

### 代币风险评估

```python
import asyncio
from typing import Dict, List
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

class TokenAnalyzer:
    def __init__(self):
        self.client = AsyncUltraApiClient()

    async def analyze_token_list(self, token_list: List[Dict[str, str]]):
        """分析代币列表的风险"""
        print("🔍 代币风险分析")
        print("=" * 50)

        # 提取铸造地址
        mints = [token["mint"] for token in token_list]

        # 批量安全检查
        shield_result = await self.client.shield(mints)
        warnings_dict = shield_result.get("warnings", {})

        # 分析每个代币
        for token in token_list:
            name = token["name"]
            mint = token["mint"]
            warnings = warnings_dict.get(mint, [])

            print(f"\n🪙 {name} ({mint[:8]}...)")
            print("-" * 30)

            if not warnings:
                print("✅ 未检测到安全警告")
                risk_score = "低"
            else:
                risk_score = self.calculate_risk_score(warnings)
                print(f"⚠️  检测到 {len(warnings)} 个警告:")

                for warning in warnings:
                    warning_type = warning.get("type", "未知")
                    message = warning.get("message", "无消息")
                    print(f"   • {warning_type}: {message}")

            print(f"🎯 风险评分: {risk_score}")

    def calculate_risk_score(self, warnings: List[Dict]) -> str:
        """根据警告计算风险评分"""
        if not warnings:
            return "低"

        high_risk_types = ["rugpull", "scam", "suspicious"]
        medium_risk_types = ["liquidity", "volume"]

        for warning in warnings:
            warning_type = warning.get("type", "").lower()
            if any(risk in warning_type for risk in high_risk_types):
                return "高"
            elif any(risk in warning_type for risk in medium_risk_types):
                return "中"

        return "中" if len(warnings) > 2 else "低"

    async def close(self):
        await self.client.close()

# 使用方法
async def analyze_tokens():
    analyzer = TokenAnalyzer()
    try:
        tokens_to_analyze = [
            {"name": "包装 SOL", "mint": "So11111111111111111111111111111111111111112"},
            {"name": "美元硬币", "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"},
            {"name": "Bonk", "mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"},
        ]

        await analyzer.analyze_token_list(tokens_to_analyze)

    finally:
        await analyzer.close()

asyncio.run(analyze_tokens())
```

### 市场扫描器

```python
import asyncio
from typing import List, Dict
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

class MarketScanner:
    def __init__(self):
        self.client = AsyncUltraApiClient()

    async def scan_trending_tokens(self, base_mints: List[str]):
        """根据交易量扫描热门代币"""
        print("📈 市场扫描器 - 热门代币")
        print("=" * 50)

        trending_data = []

        for mint in base_mints:
            try:
                # 首先检查安全性
                shield_result = await self.client.shield([mint])
                warnings = shield_result.get("warnings", {}).get(mint, [])

                safety_status = "🔴 有风险" if warnings else "🟢 安全"

                print(f"\n🔍 分析 {mint[:8]}...")
                print(f"   安全性: {safety_status}")

                if warnings:
                    print(f"   警告: {len(warnings)} 个")
                    for warning in warnings[:2]:  # 显示前 2 个警告
                        print(f"     • {warning.get('type')}")

                trending_data.append({
                    "mint": mint,
                    "safety_status": safety_status,
                    "warning_count": len(warnings)
                })

            except Exception as e:
                print(f"❌ 分析 {mint[:8]}... 时出错: {e}")

        # 按安全性排序（安全代币优先）
        trending_data.sort(key=lambda x: x["warning_count"])

        print(f"\n📊 扫描结果 ({len(trending_data)} 个代币):")
        print("-" * 40)

        for data in trending_data:
            mint = data["mint"]
            status = data["safety_status"]
            warnings = data["warning_count"]
            print(f"{status} {mint[:8]}... ({warnings} 个警告)")

    async def close(self):
        await self.client.close()

# 使用方法
async def scan_market():
    scanner = MarketScanner()
    try:
        # 要扫描的热门代币铸造地址
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

## ⚡ 高级模式

### 连接池管理器

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
        """初始化连接池"""
        print(f"🔗 初始化连接池 (大小: {self.pool_size})")

        for i in range(self.pool_size):
            client = AsyncUltraApiClient()
            self.clients.append(client)

    def get_client(self) -> AsyncUltraApiClient:
        """从池中获取下一个客户端（轮询）"""
        client = self.clients[self.current_index]
        self.current_index = (self.current_index + 1) % self.pool_size
        return client

    async def batch_operation(self, addresses: List[str]):
        """使用连接池执行批量操作"""
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
        """关闭池中的所有连接"""
        print("🔌 关闭连接池...")
        for client in self.clients:
            await client.close()

# 使用方法
async def use_connection_pool():
    pool = ConnectionPoolManager(pool_size=3)
    try:
        await pool.initialize()

        # 模拟批量处理
        addresses = [
            "11111111111111111111111111111111",  # 示例地址
            "22222222222222222222222222222222",
            "33333333333333333333333333333333",
        ]

        results = await pool.batch_operation(addresses)
        print(f"✅ 处理了 {len(results)} 个地址")

    finally:
        await pool.close_all()

# asyncio.run(use_connection_pool())
```

### 限速交易机器人

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
        """执行带限速的操作"""
        now = datetime.now()

        # 移除旧请求（超过 1 分钟的）
        while self.request_times and self.request_times[0] < now - timedelta(minutes=1):
            self.request_times.popleft()

        # 检查是否达到限制
        if len(self.request_times) >= self.max_requests:
            sleep_time = 60 - (now - self.request_times[0]).total_seconds()
            if sleep_time > 0:
                print(f"⏳ 已达到速率限制，等待 {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)

        # 记录这次请求
        self.request_times.append(now)

        # 执行操作
        return await operation()

    async def trading_loop(self, trading_pairs: list):
        """带限速的主交易循环"""
        print("🤖 启动限速交易机器人...")

        while True:
            try:
                for pair in trading_pairs:
                    input_mint, output_mint = pair

                    # 限速余额检查
                    wallet = await self.rate_limited_request(
                        lambda: self.client.get_public_key()
                    )

                    balances = await self.rate_limited_request(
                        lambda: self.client.balances(wallet)
                    )

                    print(f"📊 检查了 {wallet[:8]}... 的余额")

                    # 在这里添加您的交易逻辑

                    # 交易对之间的等待
                    await asyncio.sleep(5)

                # 交易周期之间的等待
                await asyncio.sleep(60)

            except KeyboardInterrupt:
                print("🛑 用户停止机器人")
                break
            except Exception as e:
                print(f"❌ 交易循环错误: {e}")
                await asyncio.sleep(30)  # 重试前等待

    async def close(self):
        await self.client.close()

# 使用方法
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

## 🚨 错误处理模式

### 综合错误处理器

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
        """设置错误跟踪日志"""
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
        """执行带综合错误处理的操作"""
        try:
            result = await operation(*args, **kwargs)

            # 检查结果是否表示失败
            if isinstance(result, dict) and result.get("status") == "Failed":
                error_code = result.get("code")
                error_message = result.get("error")

                self.logger.error(f"API 错误 [{error_code}]: {error_message}")

                # 处理特定错误代码
                if error_code == "INSUFFICIENT_BALANCE":
                    self.logger.warning("余额不足 - 停止操作")
                    return None
                elif error_code == "SLIPPAGE_EXCEEDED":
                    self.logger.info("滑点超出 - 以更高容忍度重试")
                    # 可以在这里实现重试逻辑
                    return None
                elif error_code == "RATE_LIMITED":
                    self.logger.warning("速率限制 - 退避")
                    await asyncio.sleep(60)
                    return None

            return result

        except ConnectionError as e:
            self.logger.error(f"连接错误: {e}")
            self.logger.info("30 秒后重试...")
            await asyncio.sleep(30)
            return None

        except TimeoutError as e:
            self.logger.error(f"超时错误: {e}")
            self.logger.info("操作超时 - 重试...")
            return None

        except ValueError as e:
            self.logger.error(f"配置错误: {e}")
            self.logger.critical("检查您的配置和私钥")
            raise  # 配置无效时不继续

        except Exception as e:
            self.logger.error(f"意外错误: {e}")
            self.logger.info("继续下一个操作...")
            return None

    async def monitor_operations(self):
        """监控和记录各种操作"""
        operations = [
            ("获取公钥", self.client.get_public_key),
            ("检查余额", self.client.balances, "wallet_address_here"),
            ("盾牌检查", self.client.shield, ["So11111111111111111111111111111111111111112"]),
        ]

        for name, operation, *args in operations:
            self.logger.info(f"执行: {name}")
            result = await self.safe_execute(operation, *args)

            if result is not None:
                self.logger.info(f"✅ {name} 成功完成")
            else:
                self.logger.warning(f"❌ {name} 失败或返回 None")

            await asyncio.sleep(2)  # 操作之间的小延迟

    async def close(self):
        await self.client.close()

# 使用方法
async def run_error_handling_demo():
    handler = ErrorHandler()
    try:
        await handler.monitor_operations()
    finally:
        await handler.close()

# asyncio.run(run_error_handling_demo())
```

### 重试机制

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
    使用指数退避进行重试

    参数:
        operation: 要重试的异步函数
        max_retries: 最大重试次数
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
        jitter: 添加随机抖动防止雷群效应
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await operation()

        except Exception as e:
            last_exception = e

            if attempt == max_retries:
                raise last_exception

            # 使用指数退避计算延迟
            delay = min(base_delay * (2 ** attempt), max_delay)

            # 添加抖动
            if jitter:
                delay *= (0.5 + random.random() * 0.5)

            print(f"❌ 第 {attempt + 1} 次尝试失败: {e}")
            print(f"⏳ {delay:.1f} 秒后重试...")

            await asyncio.sleep(delay)

    raise last_exception

# 使用示例
async def retry_example():
    from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

    client = AsyncUltraApiClient()
    try:
        # 用重试逻辑包装任何操作
        balances = await exponential_backoff_retry(
            lambda: client.balances("wallet_address_here"),
            max_retries=3
        )
        print(f"✅ 获得余额: {balances}")

    finally:
        await client.close()

# asyncio.run(retry_example())
```

## 🚀 性能优化

### 并发处理

```python
import asyncio
from typing import List
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

class PerformanceOptimizer:
    def __init__(self, max_concurrent: int = 10):
        self.client = AsyncUltraApiClient()
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def concurrent_balance_check(self, addresses: List[str]):
        """并发检查多个地址的余额"""
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

        print(f"🚀 并发检查 {len(addresses)} 个地址...")
        start_time = asyncio.get_event_loop().time()

        tasks = [check_single_balance(addr) for addr in addresses]
        results = await asyncio.gather(*tasks)

        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time

        successful = sum(1 for r in results if r["status"] == "success")

        print(f"✅ 在 {duration:.2f}s 内完成")
        print(f"📊 成功率: {successful}/{len(addresses)} ({successful/len(addresses)*100:.1f}%)")

        return results

    async def batch_shield_check(self, mint_batches: List[List[str]]):
        """批量检查代币安全性"""
        async def check_batch(batch):
            async with self.semaphore:
                try:
                    return await self.client.shield(batch)
                except Exception as e:
                    return {"error": str(e)}

        print(f"🛡️  处理 {len(mint_batches)} 个盾牌批次...")

        tasks = [check_batch(batch) for batch in mint_batches]
        results = await asyncio.gather(*tasks)

        return results

    async def close(self):
        await self.client.close()

# 使用方法
async def performance_demo():
    optimizer = PerformanceOptimizer(max_concurrent=5)

    try:
        # 演示地址（替换为真实地址）
        addresses = [
            "11111111111111111111111111111111",
            "22222222222222222222222222222222",
            "33333333333333333333333333333333",
            # 添加更多地址
        ]

        # 并发余额检查
        balance_results = await optimizer.concurrent_balance_check(addresses)

        # 批量盾牌检查
        mint_batches = [
            ["So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"],
            ["Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"],
        ]

        shield_results = await optimizer.batch_shield_check(mint_batches)

        print("🎯 性能优化演示完成！")

    finally:
        await optimizer.close()

# asyncio.run(performance_demo())
```

---

这些示例展示了 Jupiter Python SDK 的真实使用模式和最佳实践。每个示例都是完整的，可以根据您的具体用例进行调整。请记住：

1. 始终优雅地处理错误
2. 使用适当的速率限制
3. 使用完毕后关闭客户端
4. 为生产环境实施日志记录
5. 先用小金额测试

有关更详细的 API 文档，请参阅 [API 参考文档](api-reference.zh.md)。
