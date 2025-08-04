# AceFlow MCP Server 项目重构计划

## 🎯 目标结构

```
aceflow-mcp-server/
├── aceflow_mcp_server/          # 核心包目录
│   ├── core/                    # 核心功能模块
│   ├── __init__.py
│   ├── main.py                  # 主入口
│   ├── tools.py                 # 工具实现
│   ├── server.py                # 服务器实现
│   └── ...
├── tests/                       # 正式测试套件
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_tools.py
│   └── ...
├── examples/                    # 示例和演示代码
│   ├── simple_mcp_server.py
│   ├── simple_mcp_test.py
│   └── basic_usage.py
├── scripts/                     # 构建和部署脚本
│   ├── build/
│   │   ├── build_package.py
│   │   └── check_publish_readiness.py
│   ├── deploy/
│   │   ├── deploy_to_pypi.sh
│   │   └── setup_pypi_auth.sh
│   └── dev/
│       ├── setup_environment.sh
│       └── test_before_publish.sh
├── docs/                        # 文档目录
│   ├── user-guide/
│   │   ├── QUICK_START_GUIDE.md
│   │   ├── TOOL_USAGE_GUIDE.md
│   │   └── troubleshooting.md
│   ├── developer-guide/
│   │   ├── PROMPT_BEST_PRACTICES.md
│   │   ├── TOOL_PROMPTS_REVIEW.md
│   │   └── api-reference.md
│   └── project/
│       ├── COMPLETION_REPORT.md
│       └── PYPI_PUBLISH_GUIDE.md
├── dev-tests/                   # 开发测试和实验
│   ├── test_mcp_integration.py
│   ├── test_enhanced_prompts.py
│   ├── test_mcp_protocol.py
│   └── ...
├── .github/                     # GitHub 配置
│   └── workflows/
├── pyproject.toml               # 项目配置
├── README.md                    # 主要说明文档
├── LICENSE                      # 许可证
└── .gitignore                   # Git 忽略文件
```

## 📋 重构步骤

### Phase 1: 创建新目录结构
1. 创建 `examples/`, `scripts/`, `docs/`, `dev-tests/` 目录
2. 在 `scripts/` 下创建子目录：`build/`, `deploy/`, `dev/`
3. 在 `docs/` 下创建子目录：`user-guide/`, `developer-guide/`, `project/`

### Phase 2: 移动文件到合适位置
1. **示例文件** → `examples/`
2. **脚本文件** → `scripts/` 的相应子目录
3. **文档文件** → `docs/` 的相应子目录
4. **开发测试** → `dev-tests/`

### Phase 3: 清理和优化
1. 删除临时文件和生成文件
2. 更新相关路径引用
3. 更新文档中的路径引用
4. 更新 `.gitignore` 文件

### Phase 4: 验证和测试
1. 确保所有导入路径正确
2. 运行测试套件验证功能
3. 更新 CI/CD 配置
4. 更新文档链接

## 🗂️ 文件分类详情

### 移动到 `examples/`
- `simple_mcp_server.py`
- `simple_mcp_test.py`
- 其他示例代码

### 移动到 `scripts/build/`
- `build_package.py`
- `check_publish_readiness.py`

### 移动到 `scripts/deploy/`
- `build_and_publish.sh`
- `deploy_to_pypi.sh`
- `setup_pypi_auth.sh`

### 移动到 `scripts/dev/`
- `setup_environment.sh`
- `test_before_publish.sh`
- `test_uvx_install.sh`
- `diagnose_mcp.sh`

### 移动到 `docs/user-guide/`
- `QUICK_START_GUIDE.md`
- `TOOL_USAGE_GUIDE.md`

### 移动到 `docs/developer-guide/`
- `PROMPT_BEST_PRACTICES.md`
- `TOOL_PROMPTS_REVIEW.md`

### 移动到 `docs/project/`
- `COMPLETION_REPORT.md`
- `PYPI_PUBLISH_GUIDE.md`

### 移动到 `dev-tests/`
- `test_mcp_integration.py`
- `test_enhanced_prompts.py`
- `test_mcp_protocol.py`
- `test_stdio_mcp.py`
- `test_tool_registration.py`
- `test_mcp_server.py`
- `test_mcp_tools.py`
- `test_package_content.py`
- `test_mcp_async.py`
- `test_fastmcp.py`

### 删除的文件
- `coverage.json`
- `mcp_test_results.json`
- `.coverage`
- 其他临时生成文件

## 🔧 更新内容

### 更新 `pyproject.toml`
- 调整测试路径配置
- 更新包含/排除规则

### 更新 `README.md`
- 更新目录结构说明
- 更新文档链接
- 添加新的使用指南

### 更新 `.gitignore`
- 添加新的临时文件规则
- 排除开发测试的输出文件

## 📈 预期效果

### 优点
1. **清晰的结构** - 每个目录都有明确的用途
2. **易于维护** - 相关文件集中管理
3. **专业外观** - 符合开源项目标准
4. **便于导航** - 用户和开发者容易找到需要的内容

### 改进指标
- **文件组织度**: 从 6/10 提升到 9/10
- **可维护性**: 从 7/10 提升到 9/10
- **用户体验**: 从 7/10 提升到 9/10
- **开发效率**: 从 7/10 提升到 8.5/10

## ⚠️ 注意事项

1. **路径更新** - 确保所有导入和引用路径正确更新
2. **CI/CD 配置** - 更新构建和测试脚本中的路径
3. **文档链接** - 更新所有文档中的相对链接
4. **向后兼容** - 考虑现有用户的使用习惯

## 🎯 实施时间表

- **Phase 1**: 1小时 - 创建目录结构
- **Phase 2**: 2小时 - 移动文件
- **Phase 3**: 1小时 - 清理优化
- **Phase 4**: 1小时 - 验证测试

**总计**: 约 5 小时完成重构