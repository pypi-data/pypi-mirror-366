# Minecraft Wiki MCP Server

[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md) [![中文](https://img.shields.io/badge/lang-中文-red.svg)](README_CN.md)

## 项目简介

一个基于 **MCP** 的 **Minecraft Wiki** 后端服务器，提供了对 Minecraft Wiki 内容的便捷访问。现已支持通过 **uvx** 快速部署，无需复杂配置即可开始使用。

注意：本项目仅提供示例的 Minecraft wiki api，如果需要本地搭建api或需要SSE支持，请前往[此项目](https://github.com/rice-awa/minecraft-wiki-fetch-api)获取更多信息。

### 功能特性

- 🔍 **Wiki 内容搜索**: 支持关键词搜索 Minecraft Wiki 页面
- 📄 **页面内容获取**: 获取完整的页面内容，支持 HTML 和 Markdown 格式
- 📚 **批量页面获取**: 高效地批量获取多个页面内容
- ✅ **页面存在性检查**: 快速检查页面是否存在
- 🏥 **健康状态监控**: 监控后端 Wiki API 服务状态
- 🚀 **一键部署**: 支持 uvx 快速安装和运行
- ⚙️ **环境变量配置**: 灵活的配置方式，无需配置文件
- 💻 **命令行参数**: 支持命令行参数覆盖配置

## 快速开始

### 🚀 推荐方式：使用 uvx (推荐)

无需安装，直接运行：

```bash
# 基本使用（使用默认配置）
uvx mc-wiki-fetch-mcp

# 使用自定义 API 地址
MC_WIKI_API_BASE_URL=http://localhost:3000 uvx mc-wiki-fetch-mcp

# 启用详细日志
MC_WIKI_LOG_LEVEL=DEBUG uvx mc-wiki-fetch-mcp

# 使用命令行参数
uvx mc-wiki-fetch-mcp --api-url http://localhost:3000 --log-level DEBUG

# 查看帮助
uvx mc-wiki-fetch-mcp --help
```

### 💻 与 Cherry studio 集成

1. **编辑配置文件:**
   ```json
   {
     "mcpServers": {
       "minecraft-wiki": {
         "command": "uvx",
         "args": ["mc-wiki-fetch-mcp"],
         "env": {
           "MC_WIKI_API_BASE_URL": "http://mcwiki.rice-awa.top"
         }
       }
     }
   }
   ```

### 如果在 Windows 无法运行尝试以下配置
 ```json
   {
     "mcpServers": {
       "minecraft-wiki": {
         "command": "cmd",
         "args": ["uvx", "mc-wiki-fetch-mcp"],
         "env": {
           "MC_WIKI_API_BASE_URL": "http://mcwiki.rice-awa.top"
         }
       }
     }
   }
   ```

2. **更新mcp服务器**

## 配置选项

### 环境变量配置

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `MC_WIKI_API_BASE_URL` | Wiki API 基础URL | `http://mcwiki.rice-awa.top` |
| `MC_WIKI_API_TIMEOUT` | API请求超时时间(秒) | `30` |
| `MC_WIKI_API_MAX_RETRIES` | 最大重试次数 | `3` |
| `MC_WIKI_DEFAULT_FORMAT` | 默认输出格式 | `both` |
| `MC_WIKI_DEFAULT_LIMIT` | 默认搜索结果限制 | `10` |
| `MC_WIKI_MAX_BATCH_SIZE` | 最大批量处理大小 | `20` |
| `MC_WIKI_MAX_CONCURRENCY` | 最大并发数 | `5` |
| `MC_WIKI_MCP_NAME` | MCP服务器名称 | `Minecraft Wiki MCP (stdio)` |
| `MC_WIKI_MCP_DESCRIPTION` | MCP服务器描述 | 自动生成 |
| `MC_WIKI_LOG_LEVEL` | 日志级别 | `INFO` |


## 传统安装方式（开发者）

如果您需要修改代码或进行开发：

```bash
# 克隆项目
git clone <repository-url>
cd mc-wiki-fetch-mcp

# 安装依赖
pip install -e .

# 运行
mc-wiki-fetch-mcp
```

## 🛠️ 可用工具

| 工具名称 | 功能描述 | 主要参数 |
|---------|----------|----------|
| `search_wiki` | 搜索 Wiki 内容 | `query`, `limit`, `namespaces` |
| `get_wiki_page` | 获取页面内容 | `page_name`, `format`, `use_cache` |
| `get_wiki_pages_batch` | 批量获取页面 | `pages`, `format`, `concurrency` |
| `check_page_exists` | 检查页面存在 | `page_name` |
| `check_wiki_api_health` | 健康检查 | 无参数 |

### 使用示例

#### 在 Cherry studio 中使用

配置完成后，您可以在 Cherry studio 中直接询问：

```
请帮我搜索关于红石的信息
获取钻石页面的详细内容
检查"红石电路"页面是否存在
批量获取"钻石"、"红石"、"附魔"三个页面的内容
```

## 🔧 高级配置

### 配置优先级

配置的优先级顺序（从高到低）：
1. 命令行参数
2. 环境变量
3. 默认值

### 配置参数说明

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| API 基础URL | Wiki API 服务地址 | `http://mcwiki.rice-awa.top` | 任何有效 URL |
| 请求超时 | API 请求超时时间 | `30秒` | 正整数(秒) |
| 最大重试 | 失败请求重试次数 | `3次` | 正整数 |
| 默认格式 | 页面内容输出格式 | `both` | `html`, `markdown`, `both` |
| 搜索限制 | 默认搜索结果数量 | `10` | 1-50 |
| 批量大小 | 批量处理最大页面数 | `20` | 1-100 |
| 并发数 | 最大并发请求数 | `5` | 1-20 |

### 日志配置

```bash
# 不同日志级别
MC_WIKI_LOG_LEVEL=DEBUG uvx mc-wiki-fetch-mcp   # 详细调试信息
MC_WIKI_LOG_LEVEL=INFO uvx mc-wiki-fetch-mcp    # 基本信息
MC_WIKI_LOG_LEVEL=WARNING uvx mc-wiki-fetch-mcp # 仅警告和错误
MC_WIKI_LOG_LEVEL=ERROR uvx mc-wiki-fetch-mcp   # 仅错误信息
```

## 🐛 故障排除

### 常见问题

#### 1. uvx 命令不存在

**问题**: `uvx: command not found`

**解决方案**:
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# 或者使用 pip
pip install uv
```

#### 2. 无法连接到 Wiki API

**问题**: 工具调用返回连接错误

**解决方案**:
1. 检查环境变量配置：
   ```bash
   echo $MC_WIKI_API_BASE_URL
   ```
2. 测试 API 连接：
   ```bash
   curl http://your-api-url/health
   ```
3. 启用详细日志：
   ```bash
   MC_WIKI_LOG_LEVEL=DEBUG uvx mc-wiki-fetch-mcp
   ```

#### 3. Cherry studio 中不显示工具

**问题**: 配置后在 Cherry studio 中看不到 MCP 工具

**解决方案**
1. 确认 uvx 可用：
   ```bash
   uvx mc-wiki-fetch-mcp --version
   ```
2. 查看Cherry studio 日志
3. 重启 Cherry studio

### 调试技巧

#### 启用详细日志
```bash
# 启动服务器并查看详细日志
MC_WIKI_LOG_LEVEL=DEBUG uvx mc-wiki-fetch-mcp 2>debug.log

# 查看日志
tail -f debug.log
```

#### 测试配置
```bash
# 测试特定配置
MC_WIKI_API_BASE_URL=http://localhost:3000 \
MC_WIKI_LOG_LEVEL=DEBUG \
uvx mc-wiki-fetch-mcp --help
```

#### 验证环境变量
```bash
# 检查当前环境变量
env | grep MC_WIKI

# 或者在 Python 中检查
python -c "import os; print({k:v for k,v in os.environ.items() if k.startswith('MC_WIKI')})"
```

## 📖 相关文档

- [UVX 打包总结](docs/UVX_PACKAGING_SUMMARY.md) - UVX 打包和环境变量配置说明
- [API 文档](docs/API_DOCUMENTATION.md) - 详细的 API 接口说明
- [使用指南](docs/USAGE_GUIDE.md) - 深入的使用教程
- [项目完成总结](docs/PROJECT_COMPLETION_SUMMARY.md) - 项目开发总结

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进项目！

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](./LICENSE) 文件。

## 🆘 获取帮助

如果您遇到问题或需要帮助：

1. 查看本 README 的故障排除部分
2. 检查 [docs/](docs/) 目录中的详细文档
3. 提交 Issue 描述您的问题
4. 查看日志文件获取详细错误信息

---

**快速开始提示**: 
- 🚀 **推荐**: 使用 `uvx mc-wiki-fetch-mcp` 快速开始
- 💻 **Cherry studio**: 配置中使用 `uvx` 命令和环境变量
- ⚙️ **自定义**: 通过环境变量或命令行参数调整配置
- 🔧 **开发**: 克隆仓库并使用 `pip install -e .` 进行开发