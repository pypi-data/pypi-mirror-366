# MCP Git Config Server

一个专门用于 Git 仓库检测和用户名获取的 Model Context Protocol (MCP) 服务器。

**作者**: shizeying  
**创建日期**: 2025-08-04  
**版本**: 1.1.0

## 功能特性

该 MCP 服务器提供四个主要工具：

### 1. `is_git_repository`
检测指定路径（或当前目录）是否为 Git 仓库。

**参数**:
- `path` (可选): 要检查的路径，默认为当前工作目录

**返回**:
```json
{
  "is_git_repo": true,
  "path": "/path/to/check",
  "git_dir": "/path/to/check/.git",
  "error": null
}
```

### 2. `get_git_username`
从 Git 配置中获取用户名和邮箱信息。

**参数**:
- `path` (可选): Git 仓库路径，默认为当前工作目录
- `config_type` (可选): 配置类型 - "local", "global", 或 "auto" (默认)

**返回**:
```json
{
  "username": "Your Name",
  "email": "your.email@example.com",
  "config_type": "local",
  "path": "/path/to/repo",
  "is_git_repo": true,
  "error": null
}
```

### 3. `set_working_dir`
设置工作目录，后续的 Git 操作将在此目录下进行。

**参数**:
- `path`: 要设置为工作目录的路径

**返回**:
```json
{
  "success": true,
  "old_dir": "/previous/working/directory",
  "new_dir": "/new/working/directory",
  "error": null
}
```

### 4. `get_working_dir`
获取当前设置的工作目录。

**参数**: 无

**返回**:
```json
{
  "current_dir": "/current/working/directory",
  "is_custom": true,
  "error": null
}
```

## 安装方式

### 方式 1: 使用 uvx (推荐)
```bash
uvx mcp-git-config
```

### 方式 2: 使用 pip
```bash
pip install mcp-git-config
```

### 方式 3: 从源码安装
```bash
git clone https://github.com/shizeying/mcp-git-config.git
cd mcp-git-config
uv pip install -e .
```

## 使用方法

### 作为 MCP 服务器运行
```bash
# 使用 uvx
uvx mcp-git-config

# 使用 python -m
python -m mcp_git_config

# 直接使用命令
mcp-git-config
```

### 在 Claude Desktop 中配置

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "git-config": {
      "command": "uvx",
      "args": ["mcp-git-config"]
    }
  }
}
```

### 在 Zed 编辑器中配置

在 Zed 的设置中添加：

```json
{
  "assistant": {
    "default_model": {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022"
    },
    "version": "2",
    "provider": {
      "name": "anthropic",
      "type": "anthropic"
    }
  },
  "context_servers": [
    {
      "id": "git-config",
      "executable": "uvx",
      "args": ["mcp-git-config"]
    }
  ]
}
```

## 开发

### 环境设置
```bash
# 克隆仓库
git clone https://github.com/shizeying/mcp-git-config.git
cd mcp-git-config

# 安装开发依赖
uv sync --all-extras --dev

# 安装 pre-commit 钩子
uv run pre-commit install
```

### 运行测试
```bash
# 运行所有测试
uv run pytest

# 运行测试并显示覆盖率
uv run pytest --cov=mcp_git_config

# 运行 linting
uv run ruff check .
uv run ruff format .

# 类型检查
uv run mypy src/
```

### 本地测试服务器
```bash
# 运行服务器
python -m mcp_git_config

# 或者
uv run python -m mcp_git_config
```

## 技术细节

- **语言**: Python 3.8+
- **依赖管理**: uv
- **MCP 框架**: FastMCP
- **测试框架**: pytest
- **代码格式化**: ruff
- **类型检查**: mypy

## CI/CD 流水线

项目使用 GitHub Actions 进行持续集成和部署：

- **CI**: 在多个 Python 版本上运行测试、linting 和类型检查
- **发布**: 当推送 tag 时自动发布到 PyPI
- **代码质量**: 使用 pre-commit 确保代码质量

## 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。

## 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献指南。

## 支持

如果遇到问题或有功能请求，请在 [GitHub Issues](https://github.com/shizeying/mcp-git-config/issues) 中提交。