# 🚀 PocketFlow-AGUI

PocketFlow的AGUI扩展版本 - 支持前端事件回调的轻量级工作流编排框架

[![PyPI version](https://badge.fury.io/py/pocketflow-agui.svg)](https://badge.fury.io/py/pocketflow-agui)
[![Python Support](https://img.shields.io/pypi/pyversions/pocketflow-agui.svg)](https://pypi.org/project/pocketflow-agui/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 特性

- 🔄 **轻量级工作流编排** - 简洁的API设计，易于使用
- 🎯 **AGUI事件支持** - 内置前端事件回调机制
- ⚡ **同步/异步支持** - 支持同步和异步节点执行
- 🔀 **并行处理** - 支持批量和并行节点处理
- 📦 **零依赖** - 核心功能无外部依赖
- 🎨 **类型提示** - 完整的TypeScript风格类型支持

## 📦 安装

```bash
pip install pocketflow-agui
```

## 🚀 快速开始

### 基础用法

```python
from pocketflow import BaseNode, Flow

class HelloNode(BaseNode):
    def run(self, shared):
        print(f"Hello, {shared.get('name', 'World')}!")
        return "success"

# 创建工作流
flow = Flow()
flow.start_node = HelloNode()

# 执行工作流
shared_data = {"name": "PocketFlow"}
result = flow.run(shared_data)
```

### AGUI事件支持

```python
from pocketflow import BaseNode, Flow

class EventNode(BaseNode):
    def run(self, shared):
        # 发送事件到前端
        self.emit_agui_event("progress", {
            "step": "processing",
            "message": "正在处理数据...",
            "progress": 50
        })
        
        # 执行业务逻辑
        result = self.process_data(shared)
        
        # 发送完成事件
        self.emit_agui_event("complete", {
            "result": result,
            "message": "处理完成"
        })
        
        return "success"

# 设置AGUI回调
def agui_callback(event_type, data):
    print(f"前端事件: {event_type}, 数据: {data}")

flow = Flow()
flow.set_agui_callback(agui_callback)
flow.start_node = EventNode()

# 执行工作流
flow.run({"input": "test data"})
```

### 异步工作流

```python
from pocketflow import AsyncNode, AsyncFlow
import asyncio

class AsyncProcessNode(AsyncNode):
    async def run_async(self, shared):
        # 异步处理
        await asyncio.sleep(1)
        
        # 发送AGUI事件
        self.emit_agui_event("async_complete", {
            "message": "异步处理完成"
        })
        
        return "success"

# 创建异步工作流
async def main():
    flow = AsyncFlow()
    flow.start_node = AsyncProcessNode()
    
    result = await flow.run_async({"data": "async test"})
    print(f"结果: {result}")

# 运行
asyncio.run(main())
```

## 🔧 API 文档

### BaseNode

所有节点的基类，支持AGUI事件发送。

**方法:**
- `run(shared)` - 执行节点逻辑
- `set_agui_callback(callback)` - 设置AGUI回调函数
- `emit_agui_event(event_type, data)` - 发送AGUI事件

### Flow

工作流编排器，支持节点链式执行。

**方法:**
- `set_agui_callback(callback)` - 设置AGUI回调函数
- `run(shared)` - 执行工作流

### AsyncFlow

异步工作流编排器。

**方法:**
- `run_async(shared)` - 异步执行工作流

## 🙏 致谢

本项目基于 [PocketFlow](https://github.com/original-repo) 进行扩展开发，感谢原作者的贡献。

### 主要扩展功能：
- 添加了AGUI事件回调机制
- 支持前端实时状态更新
- 增强了类型提示支持

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系

如有问题，请通过 GitHub Issues 联系我们。
