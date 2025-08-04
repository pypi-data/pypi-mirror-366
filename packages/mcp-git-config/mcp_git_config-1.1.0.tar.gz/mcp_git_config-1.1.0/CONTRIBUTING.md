# 贡献指南

感谢您对 MCP Git Config Server 项目的关注！我们欢迎所有形式的贡献。

**作者**: shizeying  
**创建日期**: 2025-08-04

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能请求：

1. 在 [GitHub Issues](https://github.com/shizeying/mcp-git-config/issues) 中搜索是否已有相关问题
2. 如果没有，请创建新的 issue，并详细描述：
   - 问题的具体表现
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息（操作系统、Python 版本等）

### 提交代码

1. **Fork 项目**
   ```bash
   git clone https://github.com/your-username/mcp-git-config.git
   cd mcp-git-config
   ```

2. **设置开发环境**
   ```bash
   # 安装 uv（如果尚未安装）
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # 安装依赖
   uv sync --all-extras --dev
   
   # 安装 pre-commit 钩子
   uv run pre-commit install
   ```

3. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **进行开发**
   - 编写代码
   - 添加测试
   - 更新文档（如需要）

5. **确保代码质量**
   ```bash
   # 运行测试
   uv run pytest
   
   # 代码格式化
   uv run ruff format .
   
   # 代码检查
   uv run ruff check .
   
   # 类型检查
   uv run mypy src/
   ```

6. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

7. **推送并创建 Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 代码规范

### 提交信息格式

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
type(scope): description

[optional body]

[optional footer]
```

类型：
- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 代码重构
- `test`: 添加或修改测试
- `chore`: 维护任务

示例：
```
feat(tools): 添加递归检查 Git 仓库功能
fix(server): 修复用户名获取时的异常处理
docs(readme): 更新安装说明
```

### Python 代码规范

- 遵循 PEP 8
- 使用 ruff 进行代码格式化和检查
- 添加类型提示
- 编写有意义的文档字符串
- 保持函数和类的单一职责

### 测试规范

- 为新功能添加测试
- 保持测试覆盖率
- 使用描述性的测试名称
- 包含正常情况和边界情况的测试

## 开发工作流

### 本地测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_server.py::TestIsGitRepository::test_current_directory_is_git_repo

# 运行测试并查看覆盖率
uv run pytest --cov=mcp_git_config

# 测试服务器
python -m mcp_git_config --log-level DEBUG
```

### 构建和发布

```bash
# 构建包
uv build

# 检查包
uv run twine check dist/*

# 本地安装测试
pip install dist/*.whl
```

## 项目结构

```
mcp-git-config/
├── src/mcp_git_config/     # 主要源代码
│   ├── __init__.py
│   ├── __main__.py         # 命令行入口
│   └── server.py           # 服务器实现
├── tests/                  # 测试文件
├── .github/workflows/      # GitHub Actions
├── pyproject.toml          # 项目配置
└── README.md              # 项目说明
```

## 发布流程

项目使用自动化发布流程：

1. 所有代码合并到 `main` 分支
2. 创建版本标签：`git tag v1.0.1`
3. 推送标签：`git push origin v1.0.1`
4. GitHub Actions 自动构建并发布到 PyPI

## 获得帮助

如果您在贡献过程中遇到任何问题：

- 查看现有的 [Issues](https://github.com/shizeying/mcp-git-config/issues)
- 创建新的 issue 寻求帮助
- 联系维护者：w741069229@163.com

再次感谢您的贡献！