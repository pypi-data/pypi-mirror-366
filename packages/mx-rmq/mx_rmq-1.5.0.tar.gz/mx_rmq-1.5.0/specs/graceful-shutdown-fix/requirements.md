# 功能需求：修复优雅停机流程中调度器停止问题

## 问题描述

当前的优雅停机流程存在问题，导致 Ctrl+C 后程序无法完全关闭。从日志分析可以看出：

```
^C调度主循环被取消，正在退出...
延时调度主循环已退出
```

虽然调度主循环显示已退出，但程序整体没有完全停止，需要强制终止。

## 根本原因分析

通过代码分析发现，问题出现在 `RedisMessageQueue._graceful_shutdown()` 方法中：

1. **缺少调度器停止调用**：`_graceful_shutdown()` 方法没有显式调用 `ScheduleService.stop_delay_processing()` 方法
2. **任务清理时机问题**：调度器相关的任务（`pubsub_listener`、`periodic_fallback` 等）在 `_cleanup_tasks()` 中被取消，但调度器本身的状态没有正确设置
3. **停止顺序不当**：应该先停止调度器服务，再清理相关任务

## 用户故事

### 故事 1：开发者优雅停机
**作为** 使用 mx-rmq 的开发者  
**我希望** 当我按下 Ctrl+C 时，程序能够完全停止  
**以便** 我可以正常重启或调试应用程序  

**验收标准：**
- WHEN 用户按下 Ctrl+C 时，THEN 程序应在 30 秒内完全退出
- WHEN 调用 `await queue.stop()` 时，THEN 所有后台任务应正确停止
- WHEN 停机过程中，THEN 应输出清晰的停机进度日志
- WHEN 停机完成后，THEN 不应有任何僵尸进程或未关闭的连接

### 故事 2：调度器服务正确停止
**作为** 系统管理员  
**我希望** 延时任务调度器能够正确响应停止信号  
**以便** 确保系统资源得到正确释放  

**验收标准：**
- WHEN 收到停止信号时，THEN 调度器应设置 `is_running = False`
- WHEN 调度器停止时，THEN 所有相关的异步任务应被正确取消
- WHEN 调度器停止时，THEN Redis pubsub 连接应被正确关闭
- WHEN 调度器停止完成时，THEN 应输出确认日志

### 故事 3：停机过程监控
**作为** 运维工程师  
**我希望** 能够监控停机过程的每个步骤  
**以便** 在出现问题时快速定位原因  

**验收标准：**
- WHEN 开始停机时，THEN 应输出 "开始停止调度器服务..." 日志
- WHEN 调度器停止完成时，THEN 应输出 "调度器服务已停止" 日志
- WHEN 停机超时时，THEN 应输出警告日志并强制退出
- WHEN 停机过程中出现异常时，THEN 应记录详细的错误信息

## 技术约束

1. **向后兼容性**：修复不应破坏现有的 API 接口
2. **性能要求**：停机过程应在 30 秒内完成
3. **资源清理**：必须确保所有 Redis 连接和异步任务被正确清理
4. **日志一致性**：停机日志应与现有日志格式保持一致

## 非功能性需求

1. **可靠性**：停机成功率应达到 99.9%
2. **可观测性**：提供详细的停机过程日志
3. **超时处理**：支持停机超时保护机制
4. **异常处理**：优雅处理停机过程中的各种异常情况

## 验收测试场景

### 场景 1：正常停机流程
```python
# 启动队列
queue = RedisMessageQueue()
await queue.start_background()

# 模拟运行一段时间
await asyncio.sleep(5)

# 正常停止
start_time = time.time()
await queue.stop()
stop_time = time.time()

# 验证
assert stop_time - start_time < 30  # 30秒内完成
assert not queue.is_running()  # 确认已停止
```

### 场景 2：信号中断停机
```python
# 启动队列
queue = RedisMessageQueue()
await queue.start_background()

# 模拟 Ctrl+C
os.kill(os.getpid(), signal.SIGINT)

# 等待停机完成
await asyncio.sleep(5)

# 验证程序已完全退出
assert not queue.is_running()
```

### 场景 3：有延时任务时的停机
```python
# 启动队列并添加延时任务
queue = RedisMessageQueue()
await queue.start_background()
await queue.produce("test", {"data": "test"}, delay=60)

# 停止队列
await queue.stop()

# 验证延时任务调度器已停止
assert not queue._monitor_service.is_running
```

## 成功标准

1. **功能完整性**：所有停机相关的用户故事验收标准都得到满足
2. **测试覆盖率**：新增代码的测试覆盖率达到 95% 以上
3. **性能指标**：停机时间不超过 30 秒
4. **稳定性**：连续 100 次停机测试成功率达到 100%