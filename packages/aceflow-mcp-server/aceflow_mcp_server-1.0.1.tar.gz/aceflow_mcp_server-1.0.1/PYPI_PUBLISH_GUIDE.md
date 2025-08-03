# AceFlow MCP Server - PyPI 发布指南

本指南详细说明如何将 AceFlow MCP Server 发布到 PyPI。

## 前置条件

### 1. 环境准备
```bash
# 安装发布工具
pip install build twine wheel setuptools

# 验证工具安装
python -m build --help
twine --help
```

### 2. PyPI 账户设置
1. 注册 PyPI 账户：https://pypi.org/account/register/
2. 验证邮箱地址
3. 生成 API Token：
   - 访问 https://pypi.org/manage/account/token/
   - 创建新 token，选择 "Entire account" 范围
   - 保存生成的 token（格式：pypi-xxxxxx）

### 3. 配置认证
```bash
# 运行认证配置脚本
./setup_pypi_auth.sh

# 或手动创建 ~/.pypirc
cat > ~/.pypirc << EOF
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-api-token-here
EOF
```

## 发布流程

### 方法一：一键发布（推荐）
```bash
# 运行一键发布脚本
./deploy_to_pypi.sh
```

这个脚本会自动执行：
1. 环境准备
2. 认证配置检查
3. 测试运行
4. 包构建和发布

### 方法二：手动发布

#### 1. 运行测试
```bash
# 运行完整测试套件
python -m pytest tests/ -v --cov=aceflow_mcp_server

# 检查测试覆盖率（应该 > 80%）
python -m pytest tests/ --cov=aceflow_mcp_server --cov-report=term-missing
```

#### 2. 清理和构建
```bash
# 清理之前的构建
rm -rf dist/ build/ *.egg-info/

# 构建包
python -m build
```

#### 3. 验证包
```bash
# 检查包完整性
python -m twine check dist/*

# 验证包内容
tar -tzf dist/aceflow-mcp-server-*.tar.gz
```

#### 4. 发布到 PyPI
```bash
# 发布到 PyPI
python -m twine upload dist/*
```

## 发布后验证

### 1. 检查 PyPI 页面
访问 https://pypi.org/project/aceflow-mcp-server/ 确认：
- 包信息正确显示
- README 内容正确渲染
- 版本号正确
- 依赖关系正确

### 2. 测试安装
```bash
# 测试 pip 安装
pip install aceflow-mcp-server

# 测试 uvx 安装
uvx aceflow-mcp-server --help

# 验证命令行工具
aceflow-mcp-server --version
```

### 3. 测试 MCP 集成
在 MCP 客户端配置中添加：
```json
{
  "mcpServers": {
    "aceflow": {
      "command": "uvx",
      "args": ["aceflow-mcp-server@latest"],
      "env": {
        "ACEFLOW_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## 版本管理

### 更新版本号
1. 修改 `pyproject.toml` 中的版本号
2. 更新 `aceflow_mcp_server/__init__.py` 中的 `__version__`
3. 提交更改并创建 git tag

### 发布新版本
```bash
# 更新版本后重新构建和发布
rm -rf dist/
python -m build
python -m twine upload dist/*
```

## 故障排除

### 常见问题

#### 1. 认证失败
```
ERROR: HTTP Error 403: Invalid or non-existent authentication information
```
**解决方案：**
- 检查 ~/.pypirc 文件是否正确配置
- 确认 API token 有效且未过期
- 重新生成 API token

#### 2. 包名冲突
```
ERROR: File already exists
```
**解决方案：**
- 检查版本号是否已存在
- 更新版本号后重新发布

#### 3. 包验证失败
```
ERROR: Invalid distribution metadata
```
**解决方案：**
- 检查 pyproject.toml 格式
- 确认所有必需字段都已填写
- 运行 `twine check dist/*` 查看详细错误

#### 4. 依赖问题
```
ERROR: Could not find a version that satisfies the requirement
```
**解决方案：**
- 检查依赖版本约束
- 确认依赖包在 PyPI 上可用
- 更新依赖版本范围

### 测试环境

如果需要在测试环境中验证，可以使用 TestPyPI：

```bash
# 发布到 TestPyPI
python -m twine upload --repository testpypi dist/*

# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ aceflow-mcp-server
```

## 维护和更新

### 定期维护任务
1. 监控 PyPI 下载统计
2. 处理用户反馈和问题报告
3. 更新依赖包版本
4. 修复安全漏洞
5. 添加新功能和改进

### 文档更新
发布后记得更新：
- README.md 中的安装说明
- 项目文档
- 使用示例
- 变更日志

## 自动化发布

考虑设置 GitHub Actions 或其他 CI/CD 工具来自动化发布流程：

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

---

**注意：** 发布到 PyPI 是不可逆的操作，请确保在发布前充分测试。