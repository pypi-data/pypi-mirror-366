# MX-RMQ 使用指南

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Redis](https://img.shields.io/badge/redis-5.0+-red.svg)](https://redis.io/)

MX-RMQ 是一个高性能、可靠的基于Redis的分布式消息队列系统，支持普通消息、延时消息、优先级消息，具备完善的监控和重试机制。

## 目录

- [特性概览](#特性概览)
- [快速开始](#快速开始)
- [安装](#安装)
- [基本使用](#基本使用)
- [高级功能](#高级功能)
- [日志系统](#日志系统)
- [配置参考](#配置参考)
- [API 参考](#api-参考)
- [监控和管理](#监控和管理)
- [部署指南](#部署指南)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 特性概览

- 🚀 **高性能**: 基于Redis的内存存储，支持10,000+消息/秒的吞吐量
- 🔄 **可靠性**: 原子性Lua脚本操作，保证消息不丢失
- ⏰ **延时消息**: 支持任意时间延迟的消息调度
- 🏷️ **优先级**: 支持高、中、低优先级消息处理
- 🔁 **自动重试**: 可配置的重试机制和指数退避
- 💀 **死信队列**: 失败消息自动进入死信队列，支持人工干预
- 📊 **监控指标**: 实时监控队列状态、处理时间、吞吐率等
- 🛑 **优雅停机**: 支持优雅停机，确保消息处理完成
- 🔧 **易于使用**: 简洁的API设计，开箱即用

## 设计限制

- ❌ **不支持消费者组**: 每个topic只能被单一消费者组负载均衡消费，如需多组消费同一消息，请创建多个topic并投递多次消息

## 快速开始

启动 redis
```shell
docker run -d --name redis8 -p 6379:6379 redis:8 redis-server
```
### 30秒快速体验

```python
import asyncio
from mx_rmq import MQConfig, RedisMessageQueue

async def handle_order(payload: dict) -> None:
    """处理订单消息"""
    print(f"处理订单: {payload['order_id']}")
    # 你的业务逻辑
    await asyncio.sleep(1)

async def main():
    # 创建消息队列
    mq = RedisMessageQueue()
    
    # 注册消息处理器
    mq.register("order_created", handle_order)
    
    # 生产消息
    await mq.produce("order_created", {
        "order_id": "ORD_123",
        "user_id": 456,
        "amount": 99.99
    })
    
    # 不会阻塞
    task = await mq.start_background()  
    #阻塞下
    
    await task
if __name__ == "__main__":
    asyncio.run(main())
```

## 安装

### 使用 uv (推荐)

```bash
# 添加到现有项目
uv add mx-rmq

# 或者从源码安装
git clone https://github.com/CodingOX/mx-rmq.git
cd mx-rmq
uv sync
```

### 使用 pip

```bash
pip install mx-rmq

# 或从源码安装
pip install git+https://github.com/CodingOX/mx-rmq.git
```

### 系统要求

- Python 3.12+
- Redis 5.0+

## 基本使用

### 1. 创建消息队列

```python
from mx_rmq import MQConfig, RedisMessageQueue

# 使用默认配置
mq = RedisMessageQueue()

# 或自定义配置
config = MQConfig(
    redis_host="redis://localhost:6379",
    max_workers=10,
    task_queue_size=20
)
mq = RedisMessageQueue(config)
```

### 2. 注册消息处理器

```python
# 方式1: 使用装饰器
@mq.register("user_registration")
async def handle_user_registration(payload: dict) -> None:
    user_id = payload['user_id']
    email = payload['email']
    print(f"欢迎新用户: {user_id} ({email})")

# 方式2: 直接注册
async def handle_payment(payload: dict) -> None:
    print(f"处理支付: {payload}")

mq.register("payment_completed", handle_payment)
```

### 3. 生产消息

```python
# 生产普通消息
message_id = await mq.produce("user_registration", {
    "user_id": 12345,
    "email": "user@example.com",
    "timestamp": "2024-01-01T00:00:00Z"
})

print(f"消息已发送: {message_id}")
```

### 4. 启动消费者

```python
# 启动消费者（会阻塞，直到收到停机信号）
await mq.start_dispatch_consuming()
```

## 高级功能

### 延时消息

```python
# 5分钟后发送提醒
await mq.produce(
    topic="send_reminder",
    payload={"user_id": 123, "type": "payment_due"},
    delay=300  # 300秒后执行
)

# 1小时后发送邮件
await mq.produce(
    topic="send_email",
    payload={
        "to": "user@example.com",
        "subject": "订单确认",
        "body": "感谢您的订单..."
    },
    delay=3600  # 1小时后执行
)
```

### 优先级消息

```python
from mx_rmq import MessagePriority

# 高优先级消息（优先处理）
await mq.produce(
    topic="system_alert",
    payload={"level": "critical", "message": "系统告警"},
    priority=MessagePriority.HIGH
)

# 普通优先级（默认）
await mq.produce(
    topic="user_activity",
    payload={"user_id": 123, "action": "login"},
    priority=MessagePriority.NORMAL
)

# 低优先级消息（最后处理）
await mq.produce(
    topic="analytics_data",
    payload={"event": "page_view", "page": "/home"},
    priority=MessagePriority.LOW
)
```

### 自定义重试配置

```python
config = MQConfig(
    redis_url="redis://localhost:6379",
    max_retries=5,  # 最大重试5次
    retry_delays=[30, 60, 300, 900, 1800],  # 重试间隔：30s, 1m, 5m, 15m, 30m
    processing_timeout=300,  # 5分钟处理超时
)

mq = RedisMessageQueue(config)
```

### 消息生存时间(TTL)

```python
# 设置消息1小时后过期
await mq.produce(
    topic="temp_notification",
    payload={"message": "临时通知"},
    ttl=3600  # 1小时后过期
)
```

### 批量生产消息

```python
# 批量发送多个消息
messages = [
    {"topic": "order_created", "payload": {"order_id": f"ORD_{i}"}}
    for i in range(100)
]

for msg in messages:
    await mq.produce(msg["topic"], msg["payload"])
```

## 日志系统

MX-RMQ 使用标准的 Python logging 系统，并提供了便捷的配置函数和彩色日志支持。

### 快速开始

#### 1. 基本日志配置

```python
import logging
from mx_rmq import RedisMessageQueue

# 方式1：使用标准 logging 配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 方式2：使用 MX-RMQ 提供的便捷配置
from mx_rmq.logging import setup_basic_logging
setup_basic_logging("INFO")

# 创建消息队列
mq = RedisMessageQueue()

# 现在可以看到所有内部日志
await mq.start_dispatch_consuming()
```

#### 2. 彩色日志配置

```python
from mx_rmq.logging import setup_colored_logging

# 配置彩色日志输出
setup_colored_logging("INFO")

# 或者使用简洁的彩色日志（不显示时间戳）
from mx_rmq.logging import setup_simple_colored_logging
setup_simple_colored_logging("INFO")

# 创建消息队列
mq = RedisMessageQueue()
```

### 日志配置函数

MX-RMQ 提供了三种便捷的日志配置函数：

#### `setup_basic_logging(level="INFO")`
基本的日志配置，输出到控制台：

```python
from mx_rmq.logging import setup_basic_logging

setup_basic_logging("DEBUG")  # 设置为 DEBUG 级别
```

#### `setup_colored_logging(level="INFO")`
彩色日志配置，不同级别使用不同颜色：

```python
from mx_rmq.logging import setup_colored_logging

setup_colored_logging("INFO")
```

颜色方案：
- 🔵 **DEBUG**: 青色
- 🟢 **INFO**: 绿色  
- 🟡 **WARNING**: 黄色
- 🔴 **ERROR**: 红色
- 🟣 **CRITICAL**: 紫色

#### `setup_simple_colored_logging(level="INFO")`
简洁的彩色日志，不显示时间戳：

```python
from mx_rmq.logging import setup_simple_colored_logging

setup_simple_colored_logging("INFO")
```

### 在应用中使用日志

#### 1. 标准方式（推荐）

```python
import logging
from mx_rmq import RedisMessageQueue
from mx_rmq.logging import setup_colored_logging

# 配置彩色日志
setup_colored_logging("INFO")

# 在每个模块中使用标准方式
logger = logging.getLogger(__name__)

async def handle_order(payload: dict) -> None:
    order_id = payload.get("order_id")
    
    # 记录业务日志
    logger.info("开始处理订单", extra={"order_id": order_id})
    
    try:
        # 处理订单逻辑
        await process_order(payload)
        logger.info("订单处理成功", extra={"order_id": order_id})
        
    except Exception as e:
        logger.error("订单处理失败", extra={"order_id": order_id}, exc_info=e)
        raise

# 创建消息队列
mq = RedisMessageQueue()
mq.register("order_created", handle_order)
```

#### 2. 使用 LoggerService（向后兼容）

```python
from mx_rmq import LoggerService
from mx_rmq.logging import setup_colored_logging

# 配置彩色日志
setup_colored_logging("INFO")

# 创建日志服务
logger_service = LoggerService("PaymentService")

# 使用标准的日志接口
logger_service.logger.info("支付服务启动")

# 使用便捷方法
logger_service.log_message_event("支付开始", "msg_123", "payments", user_id=456)
logger_service.log_error("支付失败", Exception("网络错误"), payment_id="pay_789")
logger_service.log_metric("处理延迟", 150, unit="ms")
```

### 完整示例

```python
import asyncio
import logging
from mx_rmq import MQConfig, RedisMessageQueue
from mx_rmq.logging import setup_colored_logging

# 配置彩色日志
setup_colored_logging("INFO")

# 获取应用日志器
logger = logging.getLogger("OrderApp")

async def handle_order(payload: dict) -> None:
    """处理订单消息"""
    order_id = payload.get("order_id")
    
    logger.info(f"开始处理订单: {order_id}")
    
    try:
        # 模拟订单处理
        await asyncio.sleep(1)
        
        # 模拟不同的处理结果
        if order_id.endswith("error"):
            raise ValueError("订单数据无效")
        elif order_id.endswith("warn"):
            logger.warning(f"订单处理有警告: {order_id}")
        
        logger.info(f"订单处理成功: {order_id}")
        
    except Exception as e:
        logger.error(f"订单处理失败: {order_id}", exc_info=e)
        raise

async def main():
    # 创建消息队列
    mq = RedisMessageQueue()
    
    # 注册处理器
    mq.register("order_created", handle_order)
    
    # 发送一些测试消息
    await mq.produce("order_created", {"order_id": "ORD_001"})
    await mq.produce("order_created", {"order_id": "ORD_002_warn"})
    await mq.produce("order_created", {"order_id": "ORD_003_error"})
    
    # 启动消费者
    await mq.start_dispatch_consuming()

if __name__ == "__main__":
    asyncio.run(main())
```

### 日志级别说明

```python
import logging

logger = logging.getLogger("MyApp")

# DEBUG: 详细的调试信息
logger.debug("计算折扣", extra={"original_price": 100, "discount_rate": 0.1})

# INFO: 重要的业务事件
logger.info("订单支付成功", extra={"order_id": "ORD_123", "payment_id": "PAY_456"})

# WARNING: 潜在问题但不影响功能
logger.warning("库存不足", extra={"product_id": "PROD_789", "requested": 10, "available": 5})

# ERROR: 错误需要关注
logger.error("支付网关错误", extra={"order_id": "ORD_123"}, exc_info=True)

# CRITICAL: 严重错误需要立即处理
logger.critical("数据库连接失败", extra={"database": "order_db"})
```

### 环境变量配置

可以通过环境变量配置日志级别：

```bash
# 设置日志级别
export LOG_LEVEL=DEBUG

# 在应用中使用
python your_app.py
```

```python
import os
from mx_rmq.logging import setup_colored_logging

# 从环境变量读取日志级别
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_colored_logging(log_level)
```

### 日志最佳实践

#### 1. 使用结构化日志

```python
# ✅ 推荐：使用 extra 参数传递结构化数据
logger.info("订单创建", extra={
    "order_id": "ORD_123",
    "user_id": 456, 
    "amount": 99.99,
    "currency": "USD"
})

# ❌ 避免：字符串拼接
logger.info(f"用户 {user_id} 创建了订单 {order_id}，金额 {amount}")
```

#### 2. 错误处理中的日志

```python
async def handle_payment(payload: dict) -> None:
    order_id = payload.get("order_id")
    
    try:
        await process_payment(payload)
        
    except PaymentValidationError as e:
        # 业务验证错误，记录但不重试
        logger.warning("支付验证失败", extra={
            "order_id": order_id, 
            "error": str(e),
            "error_type": "validation"
        })
        raise  # 重新抛出，进入死信队列
        
    except PaymentGatewayError as e:
        # 外部服务错误，可重试
        logger.error("支付网关错误", extra={
            "order_id": order_id,
            "error": str(e),
            "error_type": "gateway",
            "retryable": True
        })
        raise  # 重新抛出，触发重试
        
    except Exception as e:
        # 未知错误，记录详细信息
        logger.error("支付处理异常", extra={
            "order_id": order_id,
            "error": str(e),
            "error_type": type(e).__name__,
            "payload": payload
        }, exc_info=True)
        raise
```

#### 3. 性能监控日志

```python
import time

async def timed_handler(payload: dict) -> None:
    start_time = time.time()
    order_id = payload.get("order_id")
    
    try:
        await process_order(payload)
        
    finally:
        processing_time = time.time() - start_time
        logger.info("订单处理完成", extra={
            "order_id": order_id,
            "processing_time": f"{processing_time:.2f}s"
        })
        
                 # 性能告警
         if processing_time > 5:
             logger.warning("订单处理时间过长", extra={
                 "order_id": order_id,
                 "processing_time": f"{processing_time:.2f}s"
             })
```

### 测试日志功能

您可以使用以下命令测试不同的日志功能：

```bash
# 测试所有日志功能（推荐）
uv run python examples/usage_sample.py test_all_logging

# 测试标准日志
uv run python examples/usage_sample.py logging

# 测试彩色日志
uv run python examples/usage_sample.py colored

# 测试简洁彩色日志
uv run python examples/usage_sample.py simple_colored

# 测试 LoggerService 兼容性
uv run python examples/usage_sample.py logger

# 测试带彩色日志的 consumer
uv run python examples/usage_sample.py consumer
```

### 常见问题

#### Q: 为什么看不到日志输出？

**A:** MX-RMQ 遵循 Python 库最佳实践，默认使用 `NullHandler`，需要用户配置日志处理器：

```python
# 解决方案1：使用便捷配置函数
from mx_rmq.logging import setup_colored_logging
setup_colored_logging("INFO")

# 解决方案2：使用标准 logging 配置
import logging
logging.basicConfig(level=logging.INFO)
```

#### Q: 如何在生产环境中使用文件日志？

**A:** 使用标准的 Python logging 配置：

```python
import logging
from logging.handlers import RotatingFileHandler

# 配置文件日志
file_handler = RotatingFileHandler(
    'app.log', 
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)

# 配置控制台日志
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 设置格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 配置根日志器
logger = logging.getLogger('mx_rmq')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
```

## 配置参考

### MQConfig 完整参数

```python
from mx_rmq import MQConfig

config = MQConfig(
    # Redis 连接配置
    redis_host="redis://localhost:6379",      # Redis连接URL
    redis_db=0,                              # Redis数据库编号 (0-15)
    redis_password=None,                     # Redis密码
    queue_prefix="",                         # 队列前缀，用于多环境隔离
    connection_pool_size=20,                 # 连接池大小
    
    # 消费者配置
    max_workers=5,                           # 最大工作协程数
    task_queue_size=8,                       # 本地任务队列大小
    
    # 消息生命周期配置
    message_ttl=86400,                       # 消息TTL（秒），默认24小时
    processing_timeout=180,                  # 消息处理超时（秒），默认3分钟
    
    # 重试配置
    max_retries=3,                           # 最大重试次数
    retry_delays=[60, 300, 1800],           # 重试延迟间隔（秒）
    
    # 死信队列配置
    enable_dead_letter=True,                 # 是否启用死信队列
    
    # 监控配置
    monitor_interval=30,                     # 监控检查间隔（秒）
    expired_check_interval=10,               # 过期消息检查间隔（秒）
    processing_monitor_interval=30,          # Processing队列监控间隔（秒）
    batch_size=100,                          # 批处理大小
)
```

### 环境变量配置

支持通过环境变量配置：

```bash
export REDIS_URL="redis://localhost:6379"
export REDIS_PASSWORD="your_password"
export MQ_MAX_WORKERS=10
export MQ_TASK_QUEUE_SIZE=20
export MQ_MESSAGE_TTL=86400
```

```python
import os
from mx_rmq import MQConfig

config = MQConfig(
    redis_host=os.getenv("REDIS_URL", "redis://localhost:6379"),
    redis_password=os.getenv("REDIS_PASSWORD"),
    max_workers=int(os.getenv("MQ_MAX_WORKERS", "5")),
    task_queue_size=int(os.getenv("MQ_TASK_QUEUE_SIZE", "8")),
    message_ttl=int(os.getenv("MQ_MESSAGE_TTL", "86400")),
)
```

## API 参考

### RedisMessageQueue 类

#### 初始化

```python
def __init__(self, config: MQConfig | None = None) -> None:
    """
    初始化消息队列
    
    Args:
        config: 消息队列配置，如为None则使用默认配置
    """
```

#### 核心方法

```python
async def produce(
    self,
    topic: str,
    payload: dict[str, Any],
    delay: int = 0,
    priority: MessagePriority = MessagePriority.NORMAL,
    ttl: int | None = None,
    message_id: str | None = None,
) -> str:
    """
    生产消息
    
    Args:
        topic: 主题名称
        payload: 消息负载（必须是可JSON序列化的字典）
        delay: 延迟执行时间（秒），0表示立即执行
        priority: 消息优先级
        ttl: 消息生存时间（秒），None使用配置默认值
        message_id: 消息ID，None则自动生成UUID
        
    Returns:
        消息ID（字符串）
        
    Raises:
        ValueError: 参数验证失败
        RedisError: Redis操作失败
    """

def register(self, topic: str, handler: Callable) -> None:
    """
    注册消息处理器
    
    Args:
        topic: 主题名称
        handler: 处理函数，必须是async函数，接受一个dict参数
        
    Raises:
        ValueError: 处理器不是可调用对象
    """

async def start_dispatch_consuming(self) -> None:
    """
    启动消息分发和消费
    
    此方法会阻塞，直到收到停机信号(SIGINT/SIGTERM)
    
    Raises:
        RuntimeError: 系统未正确初始化
        RedisError: Redis连接错误
    """

async def cleanup(self) -> None:
    """
    清理资源，关闭Redis连接池
    """
```

### Message 类

```python
@dataclass
class Message:
    """消息数据类"""
    id: str                    # 消息唯一ID
    version: str               # 消息格式版本
    topic: str                 # 主题名称  
    payload: dict[str, Any]    # 消息负载
    priority: MessagePriority  # 消息优先级
    created_at: int           # 创建时间戳（毫秒）
    meta: MessageMeta         # 消息元数据

@dataclass  
class MessageMeta:
    """消息元数据"""
    status: MessageStatus      # 消息状态
    retry_count: int          # 重试次数
    max_retries: int          # 最大重试次数
    retry_delays: list[int]   # 重试延迟配置
    last_error: str | None    # 最后一次错误信息
    expire_at: int            # 过期时间戳
    # ... 其他元数据字段
```

### 枚举类型

```python
class MessagePriority(str, Enum):
    """消息优先级"""
    HIGH = "high"      # 高优先级
    NORMAL = "normal"  # 普通优先级
    LOW = "low"        # 低优先级

class MessageStatus(str, Enum):
    """消息状态"""
    PENDING = "pending"        # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"    # 已完成
    RETRYING = "retrying"      # 重试中
    DEAD_LETTER = "dead_letter" # 死信
```

## 监控和管理

### 指标收集

```python
from mx_rmq import MetricsCollector

# 创建指标收集器
collector = MetricsCollector(redis=mq.redis, queue_prefix=config.queue_prefix)

# 收集所有指标
metrics = await collector.collect_all_metrics(["order_created", "user_registration"])

# 打印关键指标
print(f"待处理消息: {metrics['queue.order_created.pending']}")
print(f"处理中消息: {metrics['queue.order_created.processing']}")
print(f"总吞吐量: {metrics['throughput.messages_per_minute']}")
print(f"死信队列: {metrics['queue.dlq.count']}")
```

### 队列监控

```python
# 监控单个队列
queue_metrics = await collector.collect_queue_metrics(["order_created"])
print(f"订单队列状态: {queue_metrics}")

# 监控处理性能
processing_metrics = await collector.collect_processing_metrics(["order_created"])
print(f"平均处理时间: {processing_metrics['order_created.avg_processing_time']}ms")
```

### 死信队列管理

```python
# 查看死信队列
dlq_count = await mq.redis.llen("dlq:queue")
print(f"死信队列消息数: {dlq_count}")

# 获取死信消息列表
dlq_messages = await mq.redis.lrange("dlq:queue", 0, 9)  # 获取前10条
for msg_id in dlq_messages:
    payload = await mq.redis.hget("dlq:payload:map", msg_id)
    print(f"死信消息: {msg_id} - {payload}")

# 手动重试死信消息（需要自定义实现）
async def retry_dead_message(message_id: str):
    # 从死信队列获取消息
    payload_json = await mq.redis.hget("dlq:payload:map", message_id)
    if payload_json:
        # 解析消息并重新生产
        message = json.loads(payload_json)
        await mq.produce(message["topic"], message["payload"])
        # 从死信队列移除
        await mq.redis.lrem("dlq:queue", 1, message_id)
        await mq.redis.hdel("dlq:payload:map", message_id)
```

### 实时监控脚本

```python
import asyncio
import time

async def monitor_loop():
    """实时监控循环"""
    collector = MetricsCollector(redis=mq.redis)
    
    while True:
        try:
            # 收集指标
            metrics = await collector.collect_all_metrics(["order_created"])
            
            # 输出关键指标
            print(f"[{time.strftime('%H:%M:%S')}] 队列状态:")
            print(f"  待处理: {metrics.get('queue.order_created.pending', 0)}")
            print(f"  处理中: {metrics.get('queue.order_created.processing', 0)}")
            print(f"  死信队列: {metrics.get('queue.dlq.count', 0)}")
            
            # 检查告警条件
            pending = metrics.get('queue.order_created.pending', 0)
            if pending > 100:
                print(f"⚠️  告警: 待处理消息积压 ({pending})")
                
            dlq_count = metrics.get('queue.dlq.count', 0)
            if dlq_count > 10:
                print(f"🚨 告警: 死信队列消息过多 ({dlq_count})")
                
        except Exception as e:
            print(f"监控错误: {e}")
            
        await asyncio.sleep(10)  # 每10秒检查一次

# 启动监控
asyncio.create_task(monitor_loop())
```

## 部署指南

### 本地开发环境

```bash
# 1. 启动Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 2. 运行应用
python your_app.py
```

### Docker 部署

**Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制代码
COPY . .

# 启动应用
CMD ["python", "main.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    
  app:
    build: .
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379
      - MQ_MAX_WORKERS=10
    restart: unless-stopped
    
volumes:
  redis_data:
```

### 生产环境配置

**Redis 配置建议 (redis.conf):**
```conf
# 内存管理
maxmemory-policy allkeys-lru
maxmemory 2gb

# 连接管理
timeout 300
tcp-keepalive 300

# 持久化配置
save 900 1      # 900秒内至少1个key变化时保存
save 300 10     # 300秒内至少10个key变化时保存
save 60 10000   # 60秒内至少10000个key变化时保存

# AOF持久化
appendonly yes
appendfsync everysec

# 性能优化
hz 10
dynamic-hz yes
```

**应用配置:**
```python
# 生产环境配置
config = MQConfig(
    redis_url="redis://redis-cluster:6379",
    redis_password="your_secure_password",
    max_workers=20,
    task_queue_size=50,
    connection_pool_size=30,
    message_ttl=86400 * 7,  # 7天
    processing_timeout=600,  # 10分钟
    queue_prefix="prod",    # 环境隔离
)
```

### 高可用部署

**Redis Sentinel 配置:**
```python
import redis.sentinel

# 配置Sentinel
sentinels = [
    ('sentinel1', 26379),
    ('sentinel2', 26379), 
    ('sentinel3', 26379),
]

sentinel = redis.sentinel.Sentinel(sentinels, socket_timeout=0.1)

# 发现主节点
redis_master = sentinel.master_for('mymaster', socket_timeout=0.1)

# 自定义Redis连接
config = MQConfig(redis_url="")  # 留空，使用自定义连接
mq = RedisMessageQueue(config)
mq.redis = redis_master  # 使用Sentinel管理的连接
```

### 监控和告警

**Prometheus 指标暴露:**
```python
from prometheus_client import start_http_server, Gauge, Counter

# 定义指标
queue_size = Gauge('mq_queue_size', 'Queue size', ['topic', 'status'])
messages_processed = Counter('mq_messages_processed_total', 'Messages processed', ['topic', 'status'])

async def export_metrics():
    """导出Prometheus指标"""
    collector = MetricsCollector(redis=mq.redis)
    
    while True:
        metrics = await collector.collect_all_metrics(['order_created'])
        
        # 更新Prometheus指标
        queue_size.labels(topic='order_created', status='pending').set(
            metrics.get('queue.order_created.pending', 0)
        )
        queue_size.labels(topic='order_created', status='processing').set(
            metrics.get('queue.order_created.processing', 0)
        )
        
        await asyncio.sleep(30)

# 启动Prometheus HTTP服务器
start_http_server(8000)
asyncio.create_task(export_metrics())
```

## 最佳实践

### 1. 消息设计

**✅ 推荐做法:**
```python
# 消息结构清晰，包含必要的上下文信息
await mq.produce("order_created", {
    "order_id": "ORD_123456",
    "user_id": 789,
    "total_amount": 99.99,
    "currency": "USD",
    "timestamp": "2024-01-01T12:00:00Z",
    "metadata": {
        "source": "web",
        "version": "v1.0"
    }
})
```

**❌ 避免做法:**
```python
# 消息过于简单，缺少上下文
await mq.produce("process", {"id": 123})

# 消息过于复杂，包含大量数据
await mq.produce("user_update", {
    "user": {...},  # 包含用户的所有信息
    "history": [...],  # 包含完整历史记录
    "related_data": {...}  # 包含大量关联数据
})
```

### 2. 错误处理

**✅ 推荐做法:**
```python
async def handle_payment(payload: dict) -> None:
    try:
        order_id = payload["order_id"]
        amount = payload["amount"]
        
        # 参数验证
        if not order_id or amount <= 0:
            raise ValueError(f"无效的订单参数: {payload}")
            
        # 业务逻辑
        result = await process_payment(order_id, amount)
        
        # 记录成功日志
        logger.info("支付处理成功", order_id=order_id, amount=amount)
        
    except ValueError as e:
        # 参数错误，不重试
        logger.error("支付参数错误", error=str(e), payload=payload)
        raise  # 重新抛出，进入死信队列
        
    except PaymentGatewayError as e:
        # 外部服务错误，可重试
        logger.warning("支付网关错误", error=str(e), order_id=order_id)
        raise  # 重新抛出，触发重试
        
    except Exception as e:
        # 未知错误
        logger.error("支付处理失败", error=str(e), order_id=order_id)
        raise
```

### 3. 幂等性处理

```python
async def handle_order_created(payload: dict) -> None:
    order_id = payload["order_id"]
    
    # 检查是否已处理（幂等性保护）
    if await is_order_processed(order_id):
        logger.info("订单已处理，跳过", order_id=order_id)
        return
        
    try:
        # 处理订单
        await process_order(order_id)
        
        # 标记为已处理
        await mark_order_processed(order_id)
        
    except Exception as e:
        logger.error("订单处理失败", order_id=order_id, error=str(e))
        raise
```

### 4. 性能优化

**工作协程数调优:**
```python
import os
import multiprocessing

# 根据CPU核心数和IO特性调整工作协程数
cpu_count = multiprocessing.cpu_count()

config = MQConfig(
    # CPU密集型任务：工作协程数 = CPU核心数
    max_workers=cpu_count if is_cpu_intensive else cpu_count * 2,
    
    # IO密集型任务：工作协程数 = CPU核心数 * 2-4
    # max_workers=cpu_count * 3,
    
    # 任务队列大小应该大于工作协程数
    task_queue_size=max_workers * 2,
)
```

**批量处理优化:**
```python
async def handle_batch_emails(payload: dict) -> None:
    """批量处理邮件发送"""
    email_list = payload["emails"]
    
    # 分批处理，避免内存占用过大
    batch_size = 10
    for i in range(0, len(email_list), batch_size):
        batch = email_list[i:i + batch_size]
        
        # 并发发送邮件
        tasks = [send_email(email) for email in batch]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # 避免过快的请求
        await asyncio.sleep(0.1)
```

### 5. 多组消费的实现方案

由于系统不支持消费者组功能，如需实现多组消费同一消息，建议采用以下方案：

**✅ 推荐做法:**
```python
# 方案1：创建多个topic，发送多次消息
async def send_order_created(order_data: dict):
    """发送订单创建消息到多个处理组"""
    # 发送到不同的处理组
    await mq.produce("order_created_payment", order_data)    # 支付处理组
    await mq.produce("order_created_inventory", order_data)  # 库存处理组
    await mq.produce("order_created_analytics", order_data)  # 分析处理组
    await mq.produce("order_created_notification", order_data) # 通知处理组

# 注册不同的处理器
@mq.register("order_created_payment")
async def handle_payment_processing(payload: dict):
    """处理支付相关逻辑"""
    await process_payment(payload)

@mq.register("order_created_inventory")
async def handle_inventory_processing(payload: dict):
    """处理库存相关逻辑"""
    await update_inventory(payload)

@mq.register("order_created_analytics")
async def handle_analytics_processing(payload: dict):
    """处理分析相关逻辑"""
    await update_analytics(payload)

@mq.register("order_created_notification")
async def handle_notification_processing(payload: dict):
    """处理通知相关逻辑"""
    await send_notifications(payload)
```

**方案2：使用统一的分发器**
```python
# 创建一个分发器topic
@mq.register("order_created")
async def order_dispatcher(payload: dict):
    """订单消息分发器"""
    order_id = payload["order_id"]
    
    # 并发分发到各个处理组
    tasks = [
        mq.produce("order_payment", payload),
        mq.produce("order_inventory", payload),
        mq.produce("order_analytics", payload),
        mq.produce("order_notification", payload),
    ]
    
    try:
        await asyncio.gather(*tasks)
        logger.info("订单消息分发成功", order_id=order_id)
    except Exception as e:
        logger.error("订单消息分发失败", order_id=order_id, error=str(e))
        raise
```

**方案3：使用topic命名规范**
```python
# 使用统一的命名规范
TOPIC_PATTERNS = {
    "order_created": [
        "order_created.payment",
        "order_created.inventory", 
        "order_created.analytics",
        "order_created.notification"
    ]
}

async def broadcast_message(base_topic: str, payload: dict):
    """广播消息到多个相关topic"""
    topics = TOPIC_PATTERNS.get(base_topic, [base_topic])
    
    tasks = [mq.produce(topic, payload) for topic in topics]
    await asyncio.gather(*tasks)
    
    logger.info("消息广播完成", base_topic=base_topic, target_topics=topics)

# 使用示例
await broadcast_message("order_created", order_data)
```

### 6. 监控和告警

```python
async def setup_monitoring():
    """设置监控和告警"""
    collector = MetricsCollector(redis=mq.redis)
    
    while True:
        try:
            metrics = await collector.collect_all_metrics(["order_created"])
            
            # 队列积压告警
            pending = metrics.get('queue.order_created.pending', 0)
            if pending > 1000:
                await send_alert(f"队列积压严重: {pending} 条消息待处理")
                
            # 死信队列告警  
            dlq_count = metrics.get('queue.dlq.count', 0)
            if dlq_count > 50:
                await send_alert(f"死信队列消息过多: {dlq_count} 条")
                
            # 处理时间告警
            avg_time = metrics.get('processing.order_created.avg_time', 0)
            if avg_time > 30000:  # 30秒
                await send_alert(f"消息处理时间过长: {avg_time}ms")
                
        except Exception as e:
            logger.error("监控检查失败", error=str(e))
            
        await asyncio.sleep(60)  # 每分钟检查一次
```

## 故障排除

### 常见问题

#### Q1: 消息丢失怎么办？

**症状:** 发送的消息没有被处理

**可能原因:**
1. Redis 连接中断
2. 消费者没有正确启动
3. 消息处理器抛出异常但没有正确处理

**解决方案:**
```python
# 1. 检查Redis连接
try:
    await mq.redis.ping()
    print("Redis连接正常")
except Exception as e:
    print(f"Redis连接失败: {e}")

# 2. 检查消息是否在队列中
pending_count = await mq.redis.llen("order_created:pending")
processing_count = await mq.redis.llen("order_created:processing")
print(f"待处理: {pending_count}, 处理中: {processing_count}")

# 3. 检查死信队列
dlq_count = await mq.redis.llen("dlq:queue")
print(f"死信队列: {dlq_count}")
```

#### Q2: 消息处理过慢

**症状:** 队列积压，消息处理不及时

**可能原因:**
1. 工作协程数不足
2. 处理函数执行时间过长
3. Redis性能瓶颈

**解决方案:**
```python
# 1. 增加工作协程数
config = MQConfig(max_workers=20)  # 增加到20个

# 2. 优化处理函数
async def optimized_handler(payload: dict) -> None:
    # 使用异步IO
    async with aiohttp.ClientSession() as session:
        response = await session.post(url, json=payload)
    
    # 避免阻塞操作
    await asyncio.to_thread(blocking_operation, payload)

# 3. 监控处理时间
import time

async def timed_handler(payload: dict) -> None:
    start_time = time.time()
    try:
        await actual_handler(payload)
    finally:
        processing_time = time.time() - start_time
        if processing_time > 5:  # 处理时间超过5秒
            logger.warning("处理时间过长", time=processing_time, payload=payload)
```

#### Q3: 内存使用过高

**症状:** 应用内存持续增长

**可能原因:**
1. 本地队列积压
2. 消息对象没有正确释放
3. Redis连接池过大

**解决方案:**
```python
# 1. 调整队列大小
config = MQConfig(
    task_queue_size=10,  # 减少本地队列大小
    connection_pool_size=10,  # 减少连接池大小
)

# 2. 监控内存使用
import psutil
import gc

async def memory_monitor():
    while True:
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb > 500:  # 内存超过500MB
            logger.warning("内存使用过高", memory_mb=memory_mb)
            gc.collect()  # 强制垃圾回收
            
        await asyncio.sleep(60)
```

#### Q4: Redis 连接错误

**症状:** `ConnectionError`, `TimeoutError`

**解决方案:**

```python
# 1. 检查Redis配置
config = MQConfig(
    redis_url="redis://localhost:6379",
    connection_pool_size=20,
    # 添加连接重试
)

# 2. 实现连接重试
async def create_redis_with_retry(config: MQConfig, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            redis = aioredis.from_url(config.redis_host)
            await redis.ping()
            return redis
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Redis连接失败，重试中 ({attempt + 1}/{max_retries})")
            await asyncio.sleep(2 ** attempt)
```

### 性能诊断

#### 延迟分析

```python
import time
from collections import defaultdict

class PerformanceAnalyzer:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    async def analyze_handler(self, handler_name: str, handler_func):
        """分析处理器性能"""
        async def wrapped_handler(payload: dict):
            start_time = time.time()
            try:
                result = await handler_func(payload)
                return result
            finally:
                end_time = time.time()
                processing_time = (end_time - start_time) * 1000  # 毫秒
                self.metrics[handler_name].append(processing_time)
                
                # 定期输出统计信息
                if len(self.metrics[handler_name]) % 100 == 0:
                    times = self.metrics[handler_name]
                    avg_time = sum(times) / len(times)
                    max_time = max(times)
                    min_time = min(times)
                    
                    print(f"{handler_name} 性能统计 (最近100次):")
                    print(f"  平均时间: {avg_time:.2f}ms")
                    print(f"  最大时间: {max_time:.2f}ms") 
                    print(f"  最小时间: {min_time:.2f}ms")
        
        return wrapped_handler

# 使用示例
analyzer = PerformanceAnalyzer()

@mq.register("order_created")
async def handle_order(payload: dict):
    # 处理逻辑
    await process_order(payload)

# 包装处理器进行性能分析
mq.handlers["order_created"] = await analyzer.analyze_handler(
    "order_created", 
    handle_order
)
```

