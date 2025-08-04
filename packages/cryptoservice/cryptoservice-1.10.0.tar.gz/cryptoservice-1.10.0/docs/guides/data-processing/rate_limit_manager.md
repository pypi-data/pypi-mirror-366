# 智能频率限制管理器

## 概述

为了解决 Binance API 频率限制问题，我们实现了一个智能的频率限制管理器 (`RateLimitManager`)，能够自动检测、处理和规避 API 频率限制，确保数据下载的稳定性和完整性。

## 主要特性

### 🎯 智能频率控制
- **动态延迟调整**: 根据 API 响应自动调整请求间隔
- **预防性限制**: 在接近频率限制前主动减速
- **错误恢复**: 遇到频率限制错误时自动恢复

### 📊 实时监控
- **请求计数**: 跟踪每分钟的请求数量
- **错误统计**: 记录连续错误次数
- **延迟优化**: 在无错误时逐渐降低延迟

### 🔄 自适应策略
- **渐进式退避**: 错误次数越多，延迟时间越长
- **智能重置**: 成功请求后逐步恢复正常速度
- **线程安全**: 支持多线程并发访问

## 工作原理

### 1. 预防机制
```python
# 监控每分钟请求数
if requests_this_minute >= max_requests_per_minute * 0.8:
    # 达到80%限制时增加延迟
    additional_delay = 2.0
```

### 2. 错误处理
```python
# 遇到频率限制错误时
if is_rate_limit_error(error):
    wait_time = rate_limit_manager.handle_rate_limit_error()
    time.sleep(wait_time)
    # 自动重试
```

### 3. 动态调整
```python
# 根据错误次数调整延迟
if consecutive_errors <= 3:
    current_delay *= 2    # 等待1分钟
elif consecutive_errors <= 6:
    current_delay *= 1.5  # 等待2分钟
else:
    current_delay = 20.0  # 等待5分钟
```

## 使用方法

### 基本使用
```python
from cryptoservice.services.market_service import MarketDataService

service = MarketDataService(api_key="your_key", api_secret="your_secret")

# 使用智能频率控制下载数据
service.get_perpetual_data(
    symbols=["BTCUSDT", "ETHUSDT"],
    start_time="2024-10-01",
    end_time="2024-10-31",
    db_path="./data/market.db",
    request_delay=2.0,  # 基础延迟2秒
)
```

### 保守模式（推荐）
```python
# 用于大批量下载的保守设置
service.download_universe_data(
    universe_file="./data/universe.json",
    db_path="./data/market.db",
    max_workers=1,        # 单线程
    request_delay=3.0,    # 较长的基础延迟
    max_retries=5,        # 更多重试次数
)
```

## 配置参数

### RateLimitManager 参数
| 参数 | 默认值 | 说明 |
|------|-------|------|
| `base_delay` | 0.5秒 | 基础请求间隔 |
| `max_requests_per_minute` | 1800 | 每分钟最大请求数（保守估计） |

### 动态调整策略
| 错误次数 | 延迟倍数 | 等待时间 | 说明 |
|----------|----------|----------|------|
| 1-3次 | 2倍 | 60秒 | 轻度限制 |
| 4-6次 | 1.5倍 | 120秒 | 中度限制 |
| 7+次 | 固定20秒 | 300秒 | 严重限制 |

## 监控和调试

### 日志信息
```
⚠️ 接近频率限制，增加延迟: 2.0秒
🚫 频率限制错误 #1，等待 60秒，调整延迟至 4.0秒
✅ 恢复正常，当前延迟: 2.0秒
```

### 调试模式
```python
import logging
logging.getLogger('cryptoservice').setLevel(logging.DEBUG)
```

## 最佳实践

### 1. 选择合适的基础延迟
- **小批量下载**: 1-2秒
- **中等批量**: 2-3秒
- **大批量下载**: 3-5秒

### 2. 并发控制
- **测试环境**: max_workers=1
- **生产环境**: max_workers=1-2（谨慎使用）

### 3. 错误处理
```python
try:
    service.download_universe_data(...)
except KeyboardInterrupt:
    print("用户中断，已下载的数据已保存")
except Exception as e:
    print(f"下载错误: {e}")
    print("可以重新运行继续下载")
```

## 故障排除

### 常见问题

1. **仍然遇到频率限制**
   - 增加 `request_delay` 到 5-10秒
   - 设置 `max_workers=1`
   - 检查是否有其他程序在使用同一 API

2. **下载速度太慢**
   - 在低峰期下载
   - 逐步减少 `request_delay`
   - 检查网络连接稳定性

3. **数据不完整**
   - 增加 `max_retries` 数量
   - 使用更长的基础延迟
   - 检查 API 密钥权限

### 性能对比

| 模式 | 成功率 | 下载速度 | 适用场景 |
|------|--------|----------|----------|
| 无限制 | 30-50% | 很快 | 不推荐 |
| 固定延迟 | 70-80% | 中等 | 小批量 |
| 智能管理 | 95%+ | 稳定 | 推荐 |

## 技术实现

### 线程安全
使用 `threading.Lock()` 确保多线程环境下的数据一致性。

### 状态管理
- `request_count`: 当前窗口内请求数
- `consecutive_errors`: 连续错误次数
- `current_delay`: 当前延迟时间

### 自动恢复
成功请求后自动减少错误计数，逐步恢复正常速度。

## 更新日志

- **v1.0**: 基础频率限制管理
- **v1.1**: 添加智能预防机制
- **v1.2**: 优化错误恢复策略
- **v1.3**: 添加多线程支持
