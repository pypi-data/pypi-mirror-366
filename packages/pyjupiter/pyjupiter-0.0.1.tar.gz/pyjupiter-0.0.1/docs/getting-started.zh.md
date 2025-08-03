# Jupiter Python SDK 快速开始

本指南将帮助您在几分钟内开始使用 Jupiter Python SDK。

## 📋 前置要求

开始之前，请确保您具备：

- **Python 3.9+** 已安装在您的系统上
- **Solana 钱包** 并包含一些 SOL 用于交易费用
- **您钱包的私钥**（我们将向您展示如何安全地设置）

## 🛠️ 安装

### 方案 1：使用 uv（推荐）

首先，请安装 [uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation)：

```bash
# 安装 pyjupiter
uv add pyjupiter
```

## 🔑 环境设置

### 1. 设置您的私钥

您需要将 Solana 钱包的私钥设置为环境变量。SDK 支持两种格式：

#### Base58 格式（推荐）

```bash
# 导出您的私钥（Base58 格式）
export PRIVATE_KEY="your_base58_private_key_here"
```

#### Uint8 数组格式

```bash
# 或作为 uint8 数组
export PRIVATE_KEY="[10,229,131,132,213,96,74,22,...]"
```

### 2. 可选：获取 Jupiter API 密钥

要获得增强的速率限制和功能，请从 [Jupiter Portal](https://portal.jup.ag/onboard) 获取 API 密钥：

```bash
export JUPITER_API_KEY="your_api_key_here"
```

### 3. 创建 .env 文件（可选）

在开发环境中，您可以创建一个 `.env` 文件：

```env
PRIVATE_KEY=your_base58_private_key_here
JUPITER_API_KEY=your_api_key_here
```

## 🚀 您的第一次交换

让我们从一个简单的代币交换示例开始：

### 异步示例（推荐）

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

async def main():
    # 初始化客户端
    client = AsyncUltraApiClient()

    print("🔍 获取钱包地址...")
    wallet_address = await client.get_public_key()
    print(f"📍 钱包地址: {wallet_address}")

    # 创建交换订单：0.01 WSOL → USDC
    order_request = UltraOrderRequest(
        input_mint="So11111111111111111111111111111111111111112",  # WSOL
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        amount=10000000,  # 0.01 WSOL (以 lamports 为单位)
        taker=wallet_address,
    )

    try:
        print("🔄 执行交换...")
        response = await client.order_and_execute(order_request)

        if response.get("status") == "Success":
            signature = response["signature"]
            print(f"✅ 交换成功！")
            print(f"🔗 交易链接: https://solscan.io/tx/{signature}")
        else:
            print(f"❌ 交换失败: {response.get('error')}")

    except Exception as e:
        print(f"💥 错误: {e}")
    finally:
        await client.close()

# 运行异步函数
asyncio.run(main())
```

### 同步示例

```python
from pyjupiter.clients.ultra_api_client import UltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

# 初始化同步客户端
client = UltraApiClient()

print("🔍 获取钱包地址...")
wallet_address = client.get_public_key()
print(f"📍 钱包地址: {wallet_address}")

# 创建交换订单
order_request = UltraOrderRequest(
    input_mint="So11111111111111111111111111111111111111112",  # WSOL
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    amount=10000000,  # 0.01 WSOL
    taker=wallet_address,
)

try:
    print("🔄 执行交换...")
    response = client.order_and_execute(order_request)

    if response.get("status") == "Success":
        signature = response["signature"]
        print(f"✅ 交换成功！")
        print(f"🔗 交易链接: https://solscan.io/tx/{signature}")
    else:
        print(f"❌ 交换失败: {response.get('error')}")

except Exception as e:
    print(f"💥 错误: {e}")
finally:
    client.close()
```

## 📊 检查您的余额

在进行交换之前，检查您的代币余额是很有用的：

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

async def check_balances():
    client = AsyncUltraApiClient()

    try:
        # 获取您的钱包地址
        address = await client.get_public_key()
        print(f"📍 检查余额地址: {address}")

        # 获取余额
        balances = await client.balances(address)

        print("\n💰 代币余额:")
        print("-" * 40)

        for token, details in balances.items():
            amount = details.get('uiAmount', 0)
            frozen = details.get('isFrozen', False)
            status = "🧊 冻结" if frozen else "✅ 活跃"
            print(f"{token:<8} {amount:>12.6f} {status}")

    except Exception as e:
        print(f"💥 错误: {e}")
    finally:
        await client.close()

asyncio.run(check_balances())
```

## 🛡️ 检查代币安全性

交易前请务必验证代币安全性：

```python
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

async def check_token_safety():
    client = AsyncUltraApiClient()

    # 要检查的代币
    tokens = [
        "So11111111111111111111111111111111111111112",  # WSOL
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
    ]

    try:
        print("🛡️ 检查代币安全性...")
        shield_response = await client.shield(tokens)

        for mint in tokens:
            warnings = shield_response.get("warnings", {}).get(mint, [])

            if warnings:
                print(f"⚠️  {mint[:8]}... 有警告:")
                for warning in warnings:
                    print(f"   - {warning.get('type')}: {warning.get('message')}")
            else:
                print(f"✅ {mint[:8]}... 看起来安全")

    except Exception as e:
        print(f"💥 错误: {e}")
    finally:
        await client.close()

asyncio.run(check_token_safety())
```

## ⚙️ 客户端配置

### 基础配置

```python
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

# 默认配置
client = AsyncUltraApiClient()

# 使用 API 密钥
client = AsyncUltraApiClient(api_key="your_api_key")

# 自定义私钥环境变量
client = AsyncUltraApiClient(private_key_env_var="MY_PRIVATE_KEY")
```

### 高级配置

```python
# 自定义客户端设置
client = AsyncUltraApiClient(
    api_key="your_api_key",
    client_kwargs={
        "timeout": 30,  # 30 秒超时
        "verify": True,  # SSL 验证
        "headers": {
            "User-Agent": "MyApp/1.0",
        }
    }
)
```

### 使用代理

```python
# SOCKS5 代理
proxies = {"https": "socks5://user:pass@host:port"}
client = AsyncUltraApiClient(client_kwargs={"proxies": proxies})

# HTTP 代理
proxies = {
    "http": "http://proxy.example.com:8080",
    "https": "http://proxy.example.com:8080",
}
client = AsyncUltraApiClient(client_kwargs={"proxies": proxies})
```

## 🔍 常用代币地址

以下是一些用于测试的热门 Solana 代币铸造地址：

| 代币     | 符号 | 铸造地址                                       | 小数位 |
| -------- | ---- | ---------------------------------------------- | ------ |
| 包装 SOL | WSOL | `So11111111111111111111111111111111111111112`  | 9      |
| 美元硬币 | USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | 6      |
| 泰达币   | USDT | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` | 6      |
| Bonk     | BONK | `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263` | 5      |

## 💡 最佳实践

### 1. 始终关闭客户端

```python
# 使用 try/finally
client = AsyncUltraApiClient()
try:
    # 您的代码在这里
    pass
finally:
    await client.close()

# 或使用上下文管理器（如果可用）
async with AsyncUltraApiClient() as client:
    # 您的代码在这里
    pass
```

### 2. 优雅地处理错误

```python
try:
    response = await client.order_and_execute(order_request)

    if response.get("status") == "Failed":
        error_code = response.get("code")
        if error_code == "INSUFFICIENT_BALANCE":
            print("❌ 余额不足无法交换")
        elif error_code == "SLIPPAGE_EXCEEDED":
            print("❌ 超出滑点容忍度")
        else:
            print(f"❌ 交易失败: {response.get('error')}")
    else:
        print(f"✅ 成功: {response['signature']}")

except Exception as e:
    print(f"💥 意外错误: {e}")
```

### 3. 正确计算金额

```python
# 始终使用最小单位
sol_amount = 0.01  # SOL
lamports = int(sol_amount * 10**9)  # 转换为 lamports

usdc_amount = 10.0  # USDC
usdc_units = int(usdc_amount * 10**6)  # USDC 有 6 位小数
```

## 🚨 故障排除

### 常见问题

| 问题                                     | 解决方案                          |
| ---------------------------------------- | --------------------------------- |
| `ValueError: Invalid private key format` | 检查您的私钥格式（Base58 或数组） |
| `ConnectionError`                        | 检查您的网络连接和代理设置        |
| `Insufficient balance`                   | 确保您有足够的代币和 SOL 用于费用 |
| `Slippage exceeded`                      | 市场波动太大；重试或调整滑点      |

### 环境变量问题

```bash
# 检查您的环境变量是否已设置
echo $PRIVATE_KEY

# 如果为空，重新设置
export PRIVATE_KEY="your_private_key_here"
```

### 网络问题

```python
# 测试基本连接
import asyncio
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

async def test_connection():
    client = AsyncUltraApiClient()
    try:
        address = await client.get_public_key()
        print(f"✅ 连接成功！钱包: {address}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
    finally:
        await client.close()

asyncio.run(test_connection())
```

## 📚 下一步

现在您已经掌握了基础知识，探索更多高级功能：

1. **[API 参考](api-reference.zh.md)** - 完整的方法文档
2. **[代码示例](examples.zh.md)** - 实际使用案例和模式
3. **[Ultra API 文档](https://dev.jup.ag/docs/ultra-api/)** - 官方 Jupiter 文档

## 🎉 恭喜！

您已经成功设置了 Jupiter Python SDK 并进行了第一次代币交换。现在您已准备好在 Solana 上构建复杂的 DeFi 应用程序！
