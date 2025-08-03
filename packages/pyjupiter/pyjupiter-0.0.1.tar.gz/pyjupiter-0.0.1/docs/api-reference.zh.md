# API 参考文档

Jupiter Python SDK 的完整参考文档。

## 📚 目录

- [客户端类](#客户端类)
- [核心方法](#核心方法)
- [数据模型](#数据模型)
- [配置选项](#配置选项)
- [错误处理](#错误处理)
- [实用方法](#实用方法)

## 🏛️ 客户端类

### AsyncUltraApiClient

用于 Jupiter Ultra API 交互的主要异步客户端。

```python
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient

client = AsyncUltraApiClient(
    api_key="可选的API密钥",
    private_key_env_var="PRIVATE_KEY",
    client_kwargs={}
)
```

**构造函数参数：**

| 参数                  | 类型          | 默认值          | 描述                         |
| --------------------- | ------------- | --------------- | ---------------------------- |
| `api_key`             | `str \| None` | `None`          | Jupiter API 密钥用于增强功能 |
| `private_key_env_var` | `str`         | `"PRIVATE_KEY"` | 私钥的环境变量名             |
| `client_kwargs`       | `dict`        | `{}`            | 附加的 curl_cffi 客户端配置  |

### UltraApiClient

用于 Jupiter Ultra API 交互的同步客户端。

```python
from pyjupiter.clients.ultra_api_client import UltraApiClient

client = UltraApiClient(
    api_key="可选的API密钥",
    private_key_env_var="PRIVATE_KEY",
    client_kwargs={}
)
```

**构造函数参数：** 与 `AsyncUltraApiClient` 相同

## 🔧 核心方法

### order()

创建交换订单而不执行它。

#### 方法签名

```python
# 异步
async def order(self, request: UltraOrderRequest) -> dict

# 同步
def order(self, request: UltraOrderRequest) -> dict
```

#### 参数

| 参数      | 类型                | 描述         |
| --------- | ------------------- | ------------ |
| `request` | `UltraOrderRequest` | 订单请求配置 |

#### 返回值

| 字段          | 类型  | 描述                                  |
| ------------- | ----- | ------------------------------------- |
| `requestId`   | `str` | 订单的唯一标识符                      |
| `transaction` | `str` | Base64 编码的交易                     |
| `status`      | `str` | 订单状态（`"Success"` 或 `"Failed"`） |

#### 示例

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

执行先前创建的订单。

#### 方法签名

```python
# 异步
async def execute(self, request: UltraExecuteRequest) -> dict

# 同步
def execute(self, request: UltraExecuteRequest) -> dict
```

#### 参数

| 参数      | 类型                  | 描述                   |
| --------- | --------------------- | ---------------------- |
| `request` | `UltraExecuteRequest` | 包含签名交易的执行请求 |

#### 返回值

| 字段        | 类型  | 描述                                  |
| ----------- | ----- | ------------------------------------- |
| `signature` | `str` | 交易签名                              |
| `status`    | `str` | 执行状态（`"Success"` 或 `"Failed"`） |
| `error`     | `str` | 错误信息（如果失败）                  |

#### 示例

```python
from pyjupiter.models.ultra_api.ultra_execute_request_model import UltraExecuteRequest

execute_request = UltraExecuteRequest(
    request_id=response["requestId"],
    signed_transaction="base64_signed_transaction"
)

result = await client.execute(execute_request)
```

### order_and_execute()

在单次调用中创建并执行订单。

#### 方法签名

```python
# 异步
async def order_and_execute(self, request: UltraOrderRequest) -> dict

# 同步
def order_and_execute(self, request: UltraOrderRequest) -> dict
```

#### 参数

| 参数      | 类型                | 描述         |
| --------- | ------------------- | ------------ |
| `request` | `UltraOrderRequest` | 订单请求配置 |

#### 返回值

与 `execute()` 方法相同。

#### 示例

```python
response = await client.order_and_execute(order_request)
print(f"交易链接: https://solscan.io/tx/{response['signature']}")
```

### balances()

获取 Solana 地址的代币余额。

#### 方法签名

```python
# 异步
async def balances(self, address: str) -> dict

# 同步
def balances(self, address: str) -> dict
```

#### 参数

| 参数      | 类型  | 描述            |
| --------- | ----- | --------------- |
| `address` | `str` | Solana 公钥地址 |

#### 返回值

代币符号到余额详情的字典映射：

| 字段       | 类型    | 描述               |
| ---------- | ------- | ------------------ |
| `amount`   | `str`   | 最小单位的原始金额 |
| `uiAmount` | `float` | 人类可读的金额     |
| `slot`     | `int`   | 区块链槽位号       |
| `isFrozen` | `bool`  | 代币账户是否被冻结 |

#### 示例

```python
address = await client.get_public_key()
balances = await client.balances(address)

for token, details in balances.items():
    print(f"{token}: {details['uiAmount']} (冻结: {details['isFrozen']})")
```

### shield()

检查代币的安全警告。

#### 方法签名

```python
# 异步
async def shield(self, mints: list[str]) -> dict

# 同步
def shield(self, mints: list[str]) -> dict
```

#### 参数

| 参数    | 类型        | 描述             |
| ------- | ----------- | ---------------- |
| `mints` | `list[str]` | 代币铸造地址列表 |

#### 返回值

| 字段       | 类型   | 描述                     |
| ---------- | ------ | ------------------------ |
| `warnings` | `dict` | 铸造地址到警告列表的映射 |

警告对象结构：

| 字段      | 类型  | 描述     |
| --------- | ----- | -------- |
| `type`    | `str` | 警告类型 |
| `message` | `str` | 警告描述 |

#### 示例

```python
mints = [
    "So11111111111111111111111111111111111111112",  # WSOL
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
]

shield_response = await client.shield(mints)

for mint, warnings in shield_response.get("warnings", {}).items():
    if warnings:
        print(f"⚠️ {mint} 有警告:")
        for warning in warnings:
            print(f"  - {warning['type']}: {warning['message']}")
```

## 📦 数据模型

### UltraOrderRequest

用于创建交换订单的 Pydantic 模型。

#### 字段

| 字段               | 类型  | 必需 | 描述             |
| ------------------ | ----- | ---- | ---------------- |
| `input_mint`       | `str` | ✅   | 输入代币铸造地址 |
| `output_mint`      | `str` | ✅   | 输出代币铸造地址 |
| `amount`           | `int` | ✅   | 最小单位的金额   |
| `taker`            | `str` | ❌   | 接收者的公钥     |
| `referral_account` | `str` | ❌   | 推荐账户地址     |
| `referral_fee`     | `int` | ❌   | 推荐费用（基点） |

#### 示例

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

用于执行订单的 Pydantic 模型。

#### 字段

| 字段                 | 类型  | 必需 | 描述                  |
| -------------------- | ----- | ---- | --------------------- |
| `request_id`         | `str` | ✅   | 来自订单响应的请求 ID |
| `signed_transaction` | `str` | ✅   | Base64 编码的签名交易 |

#### 示例

```python
from pyjupiter.models.ultra_api.ultra_execute_request_model import UltraExecuteRequest

request = UltraExecuteRequest(
    request_id="order_request_id",
    signed_transaction="base64_encoded_transaction"
)
```

## ⚙️ 配置选项

### 客户端配置

`client_kwargs` 参数允许广泛的自定义：

#### 超时设置

```python
client = AsyncUltraApiClient(
    client_kwargs={
        "timeout": 30,  # 30 秒
    }
)
```

#### 代理配置

```python
# SOCKS5 代理
client = AsyncUltraApiClient(
    client_kwargs={
        "proxies": {"https": "socks5://user:pass@host:port"}
    }
)

# HTTP 代理
client = AsyncUltraApiClient(
    client_kwargs={
        "proxies": {
            "http": "http://proxy.example.com:8080",
            "https": "http://proxy.example.com:8080"
        }
    }
)
```

#### 自定义请求头

```python
client = AsyncUltraApiClient(
    client_kwargs={
        "headers": {
            "User-Agent": "MyApp/1.0",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
    }
)
```

#### SSL 配置

```python
client = AsyncUltraApiClient(
    client_kwargs={
        "verify": True,  # 启用 SSL 验证
        # 或自定义 CA 包
        "verify": "/path/to/ca-bundle.crt"
    }
)
```

#### DNS 配置

```python
client = AsyncUltraApiClient(
    client_kwargs={
        "resolve": ["api.jup.ag:443:1.2.3.4"],
        "dns_servers": ["1.1.1.1", "1.0.0.1"]
    }
)
```

### 环境变量

| 变量              | 描述             | 格式                       |
| ----------------- | ---------------- | -------------------------- |
| `PRIVATE_KEY`     | Solana 钱包私钥  | Base58 字符串或 uint8 数组 |
| `JUPITER_API_KEY` | Jupiter API 密钥 | 字符串                     |

#### 私钥格式

```bash
# Base58 格式（推荐）
export PRIVATE_KEY="5KQwr...xyz"

# Uint8 数组格式
export PRIVATE_KEY="[10,229,131,132,213,96,74,22,...]"
```

## 🚨 错误处理

### 常见异常

| 异常                 | 描述           | 发生时机                   |
| -------------------- | -------------- | -------------------------- |
| `ValueError`         | 无效的输入参数 | 私钥格式无效、缺少必需字段 |
| `requests.HTTPError` | HTTP 错误      | API 错误（4xx、5xx 响应）  |
| `ConnectionError`    | 网络连接问题   | 网络问题、代理问题         |
| `TimeoutError`       | 请求超时       | 请求完成时间过长           |

### 响应状态码

| 状态        | 描述         |
| ----------- | ------------ |
| `"Success"` | 操作成功完成 |
| `"Failed"`  | 操作失败     |

### 错误响应结构

失败的响应包含额外的错误信息：

| 字段     | 类型  | 描述                   |
| -------- | ----- | ---------------------- |
| `status` | `str` | 始终为 `"Failed"`      |
| `error`  | `str` | 人类可读的错误信息     |
| `code`   | `str` | 用于程序处理的错误代码 |

### 常见错误代码

| 错误代码               | 描述               | 可能的解决方案     |
| ---------------------- | ------------------ | ------------------ |
| `INSUFFICIENT_BALANCE` | 代币不足无法交换   | 检查余额，减少金额 |
| `SLIPPAGE_EXCEEDED`    | 价格变动超出容忍度 | 重试或调整滑点     |
| `INVALID_MINT`         | 无效的代币铸造地址 | 验证铸造地址       |
| `RATE_LIMITED`         | 请求过于频繁       | 在请求之间添加延迟 |

### 错误处理示例

```python
try:
    response = await client.order_and_execute(order_request)

    if response.get("status") == "Failed":
        error_code = response.get("code")
        error_message = response.get("error")

        if error_code == "INSUFFICIENT_BALANCE":
            print("❌ 余额不足无法交换")
        elif error_code == "SLIPPAGE_EXCEEDED":
            print("❌ 价格变动过大，请重试")
        else:
            print(f"❌ 错误: {error_message}")
    else:
        print(f"✅ 成功: {response['signature']}")

except ValueError as e:
    print(f"❌ 配置错误: {e}")
except requests.HTTPError as e:
    print(f"❌ API 错误: {e}")
except Exception as e:
    print(f"❌ 意外错误: {e}")
```

## 🛠️ 实用方法

### get_public_key()

获取配置钱包的公钥。

#### 方法签名

```python
# 异步
async def get_public_key(self) -> str

# 同步
def get_public_key(self) -> str
```

#### 返回值

| 类型  | 描述              |
| ----- | ----------------- |
| `str` | Base58 编码的公钥 |

#### 示例

```python
public_key = await client.get_public_key()
print(f"钱包地址: {public_key}")
```

### close()

关闭客户端并清理资源。

#### 方法签名

```python
# 异步
async def close(self) -> None

# 同步
def close(self) -> None
```

#### 示例

```python
# 使用完毕后始终关闭客户端
try:
    # 您的操作在这里
    pass
finally:
    await client.close()  # 异步客户端
    # client.close()      # 同步客户端
```

## 🔍 高级使用模式

### 速率限制

```python
import asyncio

# 用于并发请求限制的信号量
semaphore = asyncio.Semaphore(5)  # 最多 5 个并发请求

async def rate_limited_request(client, mint):
    async with semaphore:
        return await client.shield([mint])
```

### 重试逻辑

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

### 批量操作

```python
async def batch_shield_check(client, mint_lists):
    tasks = [client.shield(mints) for mints in mint_lists]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 上下文管理器模式

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

# 使用方法
async with ManagedClient(api_key="your_key") as client:
    response = await client.balances(address)
```

## 📊 性能优化建议

### 连接复用

```python
# 好的做法：为多个操作复用客户端
client = AsyncUltraApiClient()
try:
    for address in addresses:
        balances = await client.balances(address)
        # 处理余额
finally:
    await client.close()

# 避免：为每个操作创建新客户端
for address in addresses:
    client = AsyncUltraApiClient()
    balances = await client.balances(address)
    await client.close()  # 低效
```

### 并发操作

```python
# 高效的并发处理
async def process_addresses(client, addresses):
    tasks = [client.balances(addr) for addr in addresses]
    results = await asyncio.gather(*tasks)
    return results
```

### 超时配置

```python
# 为您的用例设置适当的超时
client = AsyncUltraApiClient(
    client_kwargs={
        "timeout": 10,  # 快速操作
        # "timeout": 60,  # 慢速操作
    }
)
```

---

更多示例和用例，请参阅[代码示例](examples.zh.md)文档。
