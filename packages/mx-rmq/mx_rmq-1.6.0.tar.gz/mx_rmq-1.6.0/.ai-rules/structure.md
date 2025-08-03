---
title: Project Structure
description: "定义项目的目录结构、文件组织和命名规范。"
inclusion: always
---

# 项目结构

## 总体架构

项目采用**垂直切片架构 (Vertical Slice Architecture)**，按功能模块组织代码，而非传统的技术分层。

```
mx-rmq/
├── .ai-rules/              # AI 助手指导文件
├── .trae/                   # Trae IDE 配置
├── docs/                    # 项目文档
├── examples/                # 使用示例
├── issues/                  # 问题跟踪和改进指南
├── scripts/                 # 构建和发布脚本
├── src/mx_rmq/             # 主要源代码
├── tests/                   # 测试代码
├── pyproject.toml          # 项目配置
├── README.md               # 项目说明
└── LICENSE                 # 许可证
```

## 核心源码结构 (`src/mx_rmq/`)

### 主要模块组织

```
src/mx_rmq/
├── __init__.py             # 包入口，导出公共 API
├── config.py               # 配置管理
├── constants.py            # 全局常量定义
├── message.py              # 消息模型和枚举
├── queue.py                # 主要队列接口类
│
├── core/                   # 核心业务逻辑模块
│   ├── __init__.py        # 核心模块导出
│   ├── context.py         # 队列上下文管理
│   ├── consumer.py        # 消费者服务
│   ├── dispatch.py        # 消息分发服务
│   ├── lifecycle.py       # 消息生命周期管理
│   └── schedule.py        # 调度服务（延时任务、监控）
│
├── storage/                # 存储层抽象
│   ├── __init__.py
│   ├── redis_storage.py   # Redis 存储实现
│   └── base.py            # 存储接口定义
│
├── monitoring/             # 监控和指标收集
│   ├── __init__.py
│   ├── metrics.py         # 指标收集器
│   └── models.py          # 监控数据模型
│
├── logging/                # 日志系统
│   ├── __init__.py
│   └── service.py         # 日志服务实现
│
└── resources/              # 静态资源
    ├── __init__.py
    └── lua_scripts/       # Lua 脚本文件
```

## 模块职责划分

### 核心模块 (`core/`)

#### `context.py` - 队列上下文
- **职责**: 管理队列运行时上下文，依赖注入容器
- **主要类**: `QueueContext`
- **功能**: Redis 连接管理、配置传递、服务协调

#### `consumer.py` - 消费者服务
- **职责**: 消息消费逻辑，处理器注册和调用
- **主要类**: `ConsumerService`
- **功能**: 消息处理、错误处理、重试逻辑

#### `dispatch.py` - 消息分发
- **职责**: 消息分发和并发控制
- **主要类**: `DispatchService`, `TaskItem`
- **功能**: 协程池管理、消息分发、负载均衡

#### `lifecycle.py` - 生命周期管理
- **职责**: 消息生命周期管理，状态跟踪
- **主要类**: `MessageLifecycleService`
- **功能**: 消息状态管理、超时处理、清理逻辑

#### `schedule.py` - 调度服务
- **职责**: 延时任务调度、系统监控
- **主要类**: `ScheduleService`
- **功能**: 延时消息处理、过期监控、系统健康检查

### 支撑模块

#### `storage/` - 存储层
- **设计模式**: 抽象工厂模式
- **职责**: 数据存储抽象，支持多种后端
- **扩展性**: 可支持 Redis 以外的存储后端

#### `monitoring/` - 监控系统
- **职责**: 性能指标收集、监控数据模型
- **功能**: 实时监控、性能分析、告警支持

#### `logging/` - 日志系统
- **设计模式**: 门面模式
- **职责**: 统一日志接口，支持多种日志后端
- **后端支持**: loguru, structlog, 标准 logging

#### `resources/` - 静态资源
- **职责**: Lua 脚本、配置模板等静态资源
- **组织**: 按资源类型分类存储

## 文件命名规范

### Python 文件
- **模块文件**: 使用 `snake_case` 命名
- **类文件**: 一个文件一个主要类，文件名反映类的功能
- **服务类**: 以 `Service` 后缀命名 (如 `ConsumerService`)
- **模型类**: 简洁的名词命名 (如 `Message`, `QueueMetrics`)

### 目录命名
- **功能模块**: 使用简洁的名词 (如 `core`, `storage`)
- **复数形式**: 包含多个同类文件时使用复数 (如 `resources`)

## 代码组织原则

### 垂直切片原则
- **按功能分组**: 相关功能的代码放在同一模块
- **最小依赖**: 模块间依赖关系清晰，避免循环依赖
- **高内聚**: 模块内部功能紧密相关
- **低耦合**: 模块间通过明确接口交互

### 依赖管理
- **依赖注入**: 通过 `QueueContext` 传递依赖
- **接口抽象**: 核心逻辑依赖抽象接口，不依赖具体实现
- **配置外部化**: 所有配置通过 `MQConfig` 统一管理

### 错误处理
- **早期返回**: 使用卫语句处理边界条件
- **异常分层**: 业务异常、系统异常分别处理
- **错误传播**: 明确的错误传播路径

## 测试结构 (`tests/`)

```
tests/
├── __init__.py
├── conftest.py             # pytest 配置和 fixtures
├── test_config.py          # 配置测试
├── test_integration.py     # 集成测试
├── test_message.py         # 消息模型测试
├── test_metrics.py         # 监控指标测试
└── unit/                   # 单元测试（按模块组织）
    ├── test_core/
    ├── test_storage/
    └── test_monitoring/
```

### 测试组织原则
- **镜像结构**: 测试目录结构镜像源码结构
- **功能分组**: 按功能模块组织测试用例
- **集成分离**: 单元测试和集成测试分离

## 文档结构 (`docs/`)

```
docs/
├── 设计文档.md             # 架构设计文档
├── 延时任务设计.md         # 延时任务专项设计
└── PyPI发布指南.md         # 发布流程文档
```

## 示例代码 (`examples/`)

```
examples/
├── usage_sample.py         # 基础使用示例
└── improved_usage_examples.py  # 高级功能示例
```

## 新增代码指导

### 添加新功能
1. **确定模块**: 根据功能确定所属模块
2. **接口设计**: 先设计接口，再实现功能
3. **测试驱动**: 先写测试，再写实现
4. **文档更新**: 同步更新相关文档

### 添加新模块
1. **职责明确**: 确保模块职责单一明确
2. **接口抽象**: 定义清晰的模块接口
3. **依赖管理**: 明确模块依赖关系
4. **测试覆盖**: 提供完整的测试覆盖

### 重构指导
1. **保持接口**: 重构时保持公共接口稳定
2. **渐进式**: 采用渐进式重构，避免大规模改动
3. **测试保护**: 重构前确保测试覆盖充分
4. **文档同步**: 重构后及时更新文档

## 代码风格

### Python 规范
- **PEP 8**: 严格遵循 PEP 8 代码风格
- **类型提示**: 所有公共接口必须包含类型提示
- **文档字符串**: 使用 Google 风格的 docstring
- **导入顺序**: 标准库、第三方库、本地模块

### 命名约定
- **类名**: `PascalCase` (如 `RedisMessageQueue`)
- **函数/方法**: `snake_case` (如 `start_background`)
- **常量**: `UPPER_SNAKE_CASE` (如 `DEFAULT_TIMEOUT`)
- **私有成员**: 以单下划线开头 (如 `_internal_method`)