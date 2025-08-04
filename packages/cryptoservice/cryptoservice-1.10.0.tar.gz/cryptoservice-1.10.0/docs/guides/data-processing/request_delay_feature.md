# 请求间隔功能说明

## 概述

为了避免触发 Binance API 的频率限制，我们在 `MarketDataService` 中增加了请求间隔功能。该功能可以在每次 API 请求之间添加可配置的延迟时间。

## 功能特点

- **可配置延迟**: 支持设置任意的请求间隔时间（秒）
- **线程安全**: 在多线程并发环境下正确工作
- **智能控制**: 只在需要时添加延迟，避免不必要的等待
- **详细日志**: 记录延迟信息便于调试和监控

## 使用方法

### 1. get_perpetual_data 方法

```python
from cryptoservice.services.market_service import MarketDataService
from cryptoservice.models import Freq

service = MarketDataService(api_key="your_key", api_secret="your_secret")

# 使用默认请求间隔 (0.5秒)
report = service.get_perpetual_data(
    symbols=["BTCUSDT", "ETHUSDT"],
    start_time="2024-12-01",
    end_time="2024-12-02",
    db_path="./data/market.db",
    interval=Freq.h1,
)

# 使用自定义请求间隔 (2秒)
report = service.get_perpetual_data(
    symbols=["BTCUSDT", "ETHUSDT"],
    start_time="2024-12-01",
    end_time="2024-12-02",
    db_path="./data/market.db",
    interval=Freq.h1,
    request_delay=2.0,  # 2秒间隔
)

# 无请求间隔（不推荐）
report = service.get_perpetual_data(
    symbols=["BTCUSDT", "ETHUSDT"],
    start_time="2024-12-01",
    end_time="2024-12-02",
    db_path="./data/market.db",
    interval=Freq.h1,
    request_delay=0.0,  # 无延迟
)
```

### 2. download_universe_data 方法

```python
# 下载 Universe 数据时设置请求间隔
service.download_universe_data(
    universe_file="./universe.json",
    db_path="./data/market.db",
    interval=Freq.m1,
    max_workers=4,
    request_delay=1.0,  # 1秒间隔
)
```

## 参数说明

### request_delay

- **类型**: float
- **默认值**: 0.5 秒
- **说明**: 每次 API 请求之间的延迟时间（秒）

## 推荐配置

### 根据并发数选择延迟

| 并发线程数 | 推荐延迟时间 | 说明 |
|------------|--------------|------|
| 1          | 0.2-0.5秒    | 单线程，较小延迟即可 |
| 2-4        | 0.5-1.0秒    | 中等并发，平衡速度和稳定性 |
| 5-10       | 1.0-2.0秒    | 高并发，需要更长延迟 |
| 10+        | 2.0秒以上    | 极高并发，谨慎使用 |

### 根据数据量选择延迟

- **少量数据** (< 100个交易对): 0.5秒
- **中量数据** (100-500个交易对): 1.0秒
- **大量数据** (500+个交易对): 2.0秒或更多

## 实现原理

1. **线程锁控制**: 使用 `threading.Lock()` 确保在多线程环境下正确控制请求间隔
2. **时间差计算**: 记录上次请求时间，计算与当前时间的差值
3. **智能延迟**: 只在时间差小于设定间隔时才执行延迟
4. **精确控制**: 使用 `time.sleep()` 进行精确的时间控制

## 核心代码逻辑

```python
# 用于控制请求间隔的锁和计时器
request_lock = Lock()
last_request_time = [0.0]

def process_symbol(symbol: str):
    # 控制请求间隔
    with request_lock:
        current_time = time.time()
        time_since_last = current_time - last_request_time[0]
        if time_since_last < request_delay:
            sleep_time = request_delay - time_since_last
            logger.debug(f"等待 {sleep_time:.2f}秒 - {symbol}")
            time.sleep(sleep_time)
        last_request_time[0] = time.time()

    # 执行 API 请求
    data = self._fetch_symbol_data(...)
```

## 日志输出

启用请求间隔功能后，您将看到类似的日志输出：

```
🚀 开始下载 3 个交易对的数据
📅 时间范围: 2024-12-01 到 2024-12-02
⚙️ 重试配置: 最大3次, 基础延迟1.0秒
⏱️ 请求间隔: 1.0秒
等待 0.83秒 - ETHUSDT
等待 0.91秒 - BNBUSDT
✅ BTCUSDT: 24 条记录
✅ ETHUSDT: 24 条记录
✅ BNBUSDT: 24 条记录
```

## 注意事项

1. **网络环境**: 网络延迟较高时可以适当减少请求间隔
2. **API限制**: 不同的API端点可能有不同的频率限制
3. **性能平衡**: 延迟时间越长越安全，但下载速度会相应变慢
4. **监控日志**: 注意观察是否仍有频率限制错误
5. **错误重试**: 即使设置了请求间隔，仍然保留了错误重试机制

## 故障排除

### 仍然出现频率限制错误

1. 增加 `request_delay` 值
2. 减少 `max_workers` 并发数
3. 检查网络连接稳定性

### 下载速度太慢

1. 适当减少 `request_delay` 值
2. 增加 `max_workers` 并发数（谨慎）
3. 在稳定的网络环境下运行

### 日志过多

1. 调整日志级别：`logging.getLogger().setLevel(logging.INFO)`
2. 或者禁用调试日志：`logger.debug` 输出

## 示例脚本

完整的示例脚本请参考 `example_request_delay.py`，该脚本演示了不同请求间隔配置的效果。
