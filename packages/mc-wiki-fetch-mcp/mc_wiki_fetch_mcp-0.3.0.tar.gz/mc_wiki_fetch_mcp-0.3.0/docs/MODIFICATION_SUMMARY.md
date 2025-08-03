# MCP Server 简化修改总结

## 修改概述

本次修改的目标是简化 MCP Server，删除无关的配置文件逻辑和参数解析，只保留环境变量配置。

## 主要变更

### 1. 删除的功能
- **命令行参数解析**: 移除了 `argparse` 模块和 `parse_args()` 函数
- **命令行参数覆盖逻辑**: 删除了命令行参数覆盖环境变量的逻辑
- **复杂的帮助文档**: 移除了 argparse 中的详细帮助信息

### 2. 保留的功能
- **环境变量配置**: 完整保留所有环境变量配置选项
- **核心 MCP 功能**: 所有工具和资源定义保持不变
- **日志系统**: 简化后的日志配置系统

### 3. 环境变量列表

以下环境变量仍然可用：

| 环境变量 | 默认值 | 说明 |
|---------|-------|------|
| `MC_WIKI_API_BASE_URL` | `http://mcwiki.rice-awa.top` | Wiki API 基础URL |
| `MC_WIKI_API_TIMEOUT` | `30` | API请求超时时间(秒) |
| `MC_WIKI_API_MAX_RETRIES` | `3` | 最大重试次数 |
| `MC_WIKI_DEFAULT_FORMAT` | `both` | 默认输出格式 |
| `MC_WIKI_DEFAULT_LIMIT` | `10` | 默认搜索结果限制 |
| `MC_WIKI_MAX_BATCH_SIZE` | `20` | 最大批量处理大小 |
| `MC_WIKI_MAX_CONCURRENCY` | `5` | 最大并发数 |
| `MC_WIKI_MCP_NAME` | `Minecraft Wiki MCP (stdio)` | MCP服务器名称 |
| `MC_WIKI_MCP_DESCRIPTION` | `基于stdio传输的MCP服务器...` | MCP服务器描述 |
| `MC_WIKI_LOG_LEVEL` | `INFO` | 日志级别 |

## 使用方式

### 之前（带命令行参数）
```bash
uvx mc-wiki-fetch-mcp --api-url http://localhost:3000 --log-level DEBUG
```

### 现在（仅环境变量）
```bash
MC_WIKI_API_BASE_URL=http://localhost:3000 MC_WIKI_LOG_LEVEL=DEBUG uvx mc-wiki-fetch-mcp
```

## 优势

1. **简化代码**: 减少了约60行代码，提高了可维护性
2. **容器友好**: 环境变量配置更适合容器化部署
3. **统一配置**: 移除了命令行参数和环境变量的重复配置逻辑
4. **更少依赖**: 不再需要 argparse 相关的复杂逻辑

## 测试结果

- ✅ 模块导入正常
- ✅ 语法检查通过
- ✅ 环境变量配置生效
- ✅ 所有 MCP 工具功能保持完整

修改后的代码保持了完整的功能性，同时显著简化了配置管理。