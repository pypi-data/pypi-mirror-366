# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2025.7.31.2] - 2025-07-31

### Fixed
- **Critical**: 修复图片序列化错误 `Unable to serialize unknown type: <class 'fastmcp.utilities.types.Image'>`
- 移除直接返回 MCPImage 对象的代码，改为 Base64 文本形式传输图片数据
- 确保所有返回值都是可序列化的 TextContent 对象
- 符合 MCP 官方文档的 Resources 机制要求

### Changed
- 图片数据现在默认包含完整 Base64 编码在文本反馈中
- 移除了 `process_images` 函数和相关的 MCPImage 导入
- 优化了图片处理逻辑，提高了兼容性

### Technical Details
- 根据 MCP 官方文档，图片应该通过 Resources 机制以 Base64 文本形式传输
- 修复了当用户在反馈中提供图片时的序列化问题
- 保持了所有原有功能，只是改变了图片数据的传输方式

## [2025.0721.01] - 2025-07-21

### Added
- 初始版本发布
- Web UI 界面支持
- 智能环境检测 (SSH Remote, WSL, Local)
- 图片上传和处理功能
- 命令执行功能
- 现代化深色主题
- 模块化架构设计

### Features
- 交互式用户反馈收集
- 多语言支持
- 跨平台兼容性
- 错误处理和日志记录
- 资源管理和临时文件处理
