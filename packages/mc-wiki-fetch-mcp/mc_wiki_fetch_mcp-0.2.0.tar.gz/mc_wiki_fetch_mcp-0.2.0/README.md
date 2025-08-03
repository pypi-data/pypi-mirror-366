# Minecraft Wiki MCP Server

[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md) [![中文](https://img.shields.io/badge/lang-中文-red.svg)](README_CN.md)

## Project Overview

A **MCP**-based **Minecraft Wiki** backend server that provides convenient access to Minecraft Wiki content. Now supports quick deployment via **uvx** without complex configuration.

Note: This project only provides example Minecraft wiki API. If you need local API deployment or SSE support, please visit [this project](https://github.com/rice-awa/minecraft-wiki-fetch-api) for more information.

### Features

- 🔍 **Wiki Content Search**: Search Minecraft Wiki pages by keywords
- 📄 **Page Content Retrieval**: Get complete page content in HTML and Markdown formats
- 📚 **Batch Page Retrieval**: Efficiently retrieve multiple pages in batch
- ✅ **Page Existence Check**: Quick check if a page exists
- 🏥 **Health Monitoring**: Monitor backend Wiki API service status
- 🚀 **One-Click Deployment**: Quick installation and running via uvx
- ⚙️ **Environment Variables**: Flexible configuration without config files
- 💻 **Command Line Arguments**: Override configuration via command line parameters

## Quick Start

### 🚀 Recommended: Using uvx

No installation required, run directly:

```bash
# Basic usage (with default configuration)
uvx mc-wiki-fetch-mcp

# Use custom API URL
MC_WIKI_API_BASE_URL=http://localhost:3000 uvx mc-wiki-fetch-mcp

# Enable verbose logging
MC_WIKI_LOG_LEVEL=DEBUG uvx mc-wiki-fetch-mcp

# Use command line arguments
uvx mc-wiki-fetch-mcp --api-url http://localhost:3000 --log-level DEBUG

# Show help
uvx mc-wiki-fetch-mcp --help
```

### 💻 Integration with Claude Desktop

1. **Find configuration file location:**
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

2. **Edit configuration file:**
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

3. **Restart Claude Desktop**

## Configuration Options

### Environment Variables Configuration

| Environment Variable | Description | Default Value |
|----------------------|-------------|---------------|
| `MC_WIKI_API_BASE_URL` | Wiki API base URL | `http://mcwiki.rice-awa.top` |
| `MC_WIKI_API_TIMEOUT` | API request timeout (seconds) | `30` |
| `MC_WIKI_API_MAX_RETRIES` | Maximum retry attempts | `3` |
| `MC_WIKI_DEFAULT_FORMAT` | Default output format | `both` |
| `MC_WIKI_DEFAULT_LIMIT` | Default search results limit | `10` |
| `MC_WIKI_MAX_BATCH_SIZE` | Maximum batch processing size | `20` |
| `MC_WIKI_MAX_CONCURRENCY` | Maximum concurrency | `5` |
| `MC_WIKI_MCP_NAME` | MCP server name | `Minecraft Wiki MCP (stdio)` |
| `MC_WIKI_MCP_DESCRIPTION` | MCP server description | Auto-generated |
| `MC_WIKI_LOG_LEVEL` | Log level | `INFO` |

### Command Line Arguments

```bash
uvx mc-wiki-fetch-mcp --help
```

| Parameter | Description |
|-----------|-------------|
| `--api-url` | Wiki API base URL (overrides environment variable) |
| `--timeout` | API request timeout (seconds) |
| `--max-retries` | Maximum retry attempts |
| `--log-level` | Log level (DEBUG/INFO/WARNING/ERROR) |
| `--version` | Show version information |
| `--help` | Show help information |

## Configuration Examples

### Basic Configuration Example

```bash
# Set environment variables
export MC_WIKI_API_BASE_URL="http://localhost:3000"
export MC_WIKI_LOG_LEVEL="DEBUG"

# Run server
uvx mc-wiki-fetch-mcp
```

### Claude Desktop Advanced Configuration

```json
{
  "mcpServers": {
    "minecraft-wiki": {
      "command": "uvx",
      "args": [
        "mc-wiki-fetch-mcp",
        "--api-url", "http://localhost:3000",
        "--log-level", "INFO"
      ],
      "env": {
        "MC_WIKI_DEFAULT_LIMIT": "20",
        "MC_WIKI_MAX_BATCH_SIZE": "50"
      }
    }
  }
}
```

## Traditional Installation (Developers)

If you need to modify code or develop:

```bash
# Clone repository
git clone <repository-url>
cd mc-wiki-fetch-mcp

# Install dependencies
pip install -e .

# Run
mc-wiki-fetch-mcp
```

## 🛠️ Available Tools

| Tool Name | Description | Main Parameters |
|-----------|-------------|-----------------|
| `search_wiki` | Search Wiki content | `query`, `limit`, `namespaces` |
| `get_wiki_page` | Get page content | `page_name`, `format`, `use_cache` |
| `get_wiki_pages_batch` | Batch get pages | `pages`, `format`, `concurrency` |
| `check_page_exists` | Check page existence | `page_name` |
| `check_wiki_api_health` | Health check | No parameters |

### Usage Examples

#### Using in Claude Desktop

After configuration, you can directly ask in Claude Desktop:

```
Please help me search for information about redstone
Get detailed content of the diamond page
Check if the "redstone circuit" page exists
Batch get content for "diamond", "redstone", and "enchanting" pages
```

## 🔧 Advanced Configuration

### Configuration Priority

Configuration priority order (high to low):
1. Command line arguments
2. Environment variables
3. Default values

### Configuration Parameter Description

| Parameter | Description | Default Value | Optional Values |
|-----------|-------------|---------------|-----------------|
| API Base URL | Wiki API service address | `http://mcwiki.rice-awa.top` | Any valid URL |
| Request Timeout | API request timeout | `30 seconds` | Positive integer (seconds) |
| Maximum Retries | Failed request retry count | `3 times` | Positive integer |
| Default Format | Page content output format | `both` | `html`, `markdown`, `both` |
| Search Limit | Default search result count | `10` | 1-50 |
| Batch Size | Maximum pages for batch processing | `20` | 1-100 |
| Concurrency | Maximum concurrent requests | `5` | 1-20 |

### Log Configuration

```bash
# Different log levels
MC_WIKI_LOG_LEVEL=DEBUG uvx mc-wiki-fetch-mcp   # Detailed debug information
MC_WIKI_LOG_LEVEL=INFO uvx mc-wiki-fetch-mcp    # Basic information
MC_WIKI_LOG_LEVEL=WARNING uvx mc-wiki-fetch-mcp # Only warnings and errors
MC_WIKI_LOG_LEVEL=ERROR uvx mc-wiki-fetch-mcp   # Only errors
```

## 🐛 Troubleshooting

### Common Issues

#### 1. uvx command not found

**Problem**: `uvx: command not found`

**Solution**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or use pip
pip install uv
```

#### 2. Cannot connect to Wiki API

**Problem**: Tool calls return connection errors

**Solution**:
1. Check environment variable configuration:
   ```bash
   echo $MC_WIKI_API_BASE_URL
   ```
2. Test API connection:
   ```bash
   curl http://your-api-url/health
   ```
3. Enable verbose logging:
   ```bash
   MC_WIKI_LOG_LEVEL=DEBUG uvx mc-wiki-fetch-mcp
   ```

#### 3. Tools not showing in Claude Desktop

**Problem**: After configuration, MCP tools are not visible in Claude Desktop

**Solution**:
1. Confirm uvx is available:
   ```bash
   uvx mc-wiki-fetch-mcp --version
   ```
2. Check Claude Desktop logs
3. Restart Claude Desktop

### Debugging Tips

#### Enable Verbose Logging
```bash
# Start server and view detailed logs
MC_WIKI_LOG_LEVEL=DEBUG uvx mc-wiki-fetch-mcp 2>debug.log

# View logs
tail -f debug.log
```

#### Test Configuration
```bash
# Test specific configuration
MC_WIKI_API_BASE_URL=http://localhost:3000 \
MC_WIKI_LOG_LEVEL=DEBUG \
uvx mc-wiki-fetch-mcp --help
```

#### Verify Environment Variables
```bash
# Check current environment variables
env | grep MC_WIKI

# Or check in Python
python -c "import os; print({k:v for k,v in os.environ.items() if k.startswith('MC_WIKI')})"
```

## 📖 Related Documentation

- [UVX Packaging Summary](docs/UVX_PACKAGING_SUMMARY.md) - UVX packaging and environment variable configuration
- [API Documentation](docs/API_DOCUMENTATION.md) - Detailed API interface documentation
- [Usage Guide](docs/USAGE_GUIDE.md) - In-depth usage tutorial
- [Project Completion Summary](docs/PROJECT_COMPLETION_SUMMARY.md) - Project development summary

## 🤝 Contributing

Welcome to submit Issues and Pull Requests to improve the project!

## 📄 License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) file for details.

## 🆘 Getting Help

If you encounter problems or need help:

1. Check the troubleshooting section of this README
2. Check detailed documentation in the [docs/](docs/) directory
3. Submit an Issue describing your problem
4. Check log files for detailed error information

---

**Quick Start Tips**: 
- 🚀 **Recommended**: Use `uvx mc-wiki-fetch-mcp` to get started quickly
- 💻 **Claude Desktop**: Use `uvx` command and environment variables in configuration
- ⚙️ **Customize**: Adjust configuration through environment variables or command line arguments
- 🔧 **Development**: Clone repository and use `pip install -e .` for development