# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-08-01

### Added
- 🎯 **AGUI事件支持** - 为所有节点添加了前端事件回调机制
- 📡 **实时状态更新** - 支持向前端发送实时进度和状态信息
- 🔄 **事件传播** - 工作流自动将AGUI回调传递给所有子节点
- 🎨 **类型提示** - 添加了完整的类型提示支持
- 📦 **独立包** - 基于原始PocketFlow创建独立的AGUI扩展版本

### Enhanced
- ⚡ **BaseNode扩展** - 添加了 `set_agui_callback()` 和 `emit_agui_event()` 方法
- 🔀 **Flow增强** - 自动将AGUI回调传递给工作流中的所有节点
- 🚀 **AsyncFlow支持** - 异步工作流也支持AGUI事件回调

### Technical Details
- 添加了 `agui_callback` 属性到 `BaseNode` 类
- 实现了事件发送机制，支持任意事件类型和数据结构
- 保持了与原始PocketFlow的完全兼容性
- 支持Python 3.8+

### Breaking Changes
- 无破坏性变更，完全向后兼容

## [Unreleased]

### Planned
- 📊 更多内置事件类型
- 🔧 事件过滤和转换功能
- 📈 性能监控事件
- 🎛️ 配置化事件管理
