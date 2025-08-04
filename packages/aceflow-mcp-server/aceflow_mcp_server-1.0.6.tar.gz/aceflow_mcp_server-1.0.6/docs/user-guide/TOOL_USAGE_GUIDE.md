# AceFlow MCP 工具使用指南

本指南为大模型和开发者提供详细的 AceFlow MCP 工具使用说明。

## 🚀 工具概览

AceFlow MCP Server 提供 4 个核心工具，用于管理AI驱动的软件开发工作流：

| 工具 | 功能 | 使用场景 |
|------|------|----------|
| `aceflow_init` | 项目初始化 | 创建新项目时 |
| `aceflow_stage` | 阶段管理 | 跟踪项目进度 |
| `aceflow_validate` | 质量验证 | 检查项目合规性 |
| `aceflow_template` | 模板管理 | 配置工作流模板 |

## 📋 详细工具说明

### 1. aceflow_init - 项目初始化工具

**描述**: 🚀 初始化 AceFlow 项目 - 创建AI驱动的软件开发工作流项目结构

**何时使用**:
- 开始一个新的软件项目
- 需要建立标准化开发流程
- 想要使用AI辅助的项目管理

**参数说明**:
- `mode` (必需): 项目工作流模式
  - `minimal`: 快速原型模式 (3个阶段)
  - `standard`: 标准开发模式 (8个阶段) - **推荐**
  - `complete`: 企业级模式 (12个阶段)
  - `smart`: AI增强模式 (10个阶段)
- `project_name` (可选): 项目名称
- `directory` (可选): 项目目录路径

**使用示例**:
```json
// 创建标准Web应用项目
{
  "mode": "standard",
  "project_name": "my-web-app"
}

// 快速原型开发
{
  "mode": "minimal",
  "project_name": "prototype"
}
```

### 2. aceflow_stage - 阶段管理工具

**描述**: 📊 管理项目阶段和工作流 - 跟踪和控制项目开发进度

**何时使用**:
- 查看项目当前进度和状态
- 了解项目的工作流阶段
- 推进项目到下一个阶段

**参数说明**:
- `action` (必需): 要执行的操作
  - `list`: 列出所有可用的工作流阶段
  - `status`: 查看当前项目状态和进度
  - `next`: 推进到下一个阶段
  - `reset`: 重置项目状态到初始阶段
- `stage` (可选): 特定阶段名称

**标准工作流阶段**:
1. `user_stories` - 用户故事分析
2. `task_breakdown` - 任务分解
3. `test_design` - 测试用例设计
4. `implementation` - 功能实现
5. `unit_test` - 单元测试
6. `integration_test` - 集成测试
7. `code_review` - 代码审查
8. `demo` - 功能演示

**使用示例**:
```json
// 查看项目当前状态
{
  "action": "status"
}

// 列出所有工作流阶段
{
  "action": "list"
}

// 推进到下一阶段
{
  "action": "next"
}
```

### 3. aceflow_validate - 质量验证工具

**描述**: ✅ 验证项目合规性和质量 - 检查项目是否符合AceFlow标准和最佳实践

**何时使用**:
- 检查项目配置是否正确
- 验证代码质量和结构
- 确保项目符合标准
- 生成质量报告

**参数说明**:
- `mode` (可选): 验证模式，默认 `basic`
  - `basic`: 基础验证 - 检查核心配置和结构
  - `detailed`: 详细验证 - 深度分析代码质量和最佳实践
- `fix` (可选): 是否自动修复发现的问题，默认 `false`
- `report` (可选): 是否生成详细的验证报告，默认 `false`

**验证内容**:
- 项目结构完整性
- 配置文件正确性
- 代码质量标准
- 文档完整性
- 测试覆盖率
- 安全性检查

**使用示例**:
```json
// 基础项目验证
{
  "mode": "basic"
}

// 详细验证并生成报告
{
  "mode": "detailed",
  "report": true
}

// 验证并自动修复问题
{
  "mode": "basic",
  "fix": true
}
```

### 4. aceflow_template - 模板管理工具

**描述**: 📋 管理工作流模板 - 查看和应用不同的项目模板配置

**何时使用**:
- 查看可用的项目模板
- 应用特定模板到项目
- 验证模板配置
- 切换项目模板

**参数说明**:
- `action` (必需): 要执行的模板操作
  - `list`: 列出所有可用模板
  - `apply`: 应用指定模板到当前项目
  - `validate`: 验证模板配置
- `template` (可选): 模板名称 (apply和validate操作需要)
  - `minimal`: 最小化模板 (3个阶段)
  - `standard`: 标准模板 (8个阶段)
  - `complete`: 完整模板 (12个阶段)
  - `smart`: 智能模板 (10个阶段)

**使用示例**:
```json
// 查看所有可用模板
{
  "action": "list"
}

// 应用标准模板
{
  "action": "apply",
  "template": "standard"
}

// 验证智能模板配置
{
  "action": "validate",
  "template": "smart"
}
```

## 🎯 最佳实践建议

### 项目初始化流程
1. 使用 `aceflow_init` 创建项目 (推荐 `standard` 模式)
2. 使用 `aceflow_stage` 查看工作流阶段
3. 使用 `aceflow_validate` 验证项目配置

### 日常开发流程
1. 使用 `aceflow_stage` 查看当前状态
2. 完成当前阶段的工作
3. 使用 `aceflow_validate` 验证质量
4. 使用 `aceflow_stage` 推进到下一阶段

### 项目管理流程
1. 定期使用 `aceflow_validate` 检查项目质量
2. 使用 `aceflow_template` 管理工作流配置
3. 根据项目需要调整模板设置

## 🔄 工具使用模式

### 顺序模式 (推荐新手)
```
1. aceflow_init → 2. aceflow_stage → 3. aceflow_validate → 4. aceflow_template
```

### 并行模式 (适合有经验用户)
- `aceflow_stage` 和 `aceflow_validate` 可以并行使用
- `aceflow_template` 可以在任何阶段调整
- 定期使用 `aceflow_validate` 确保质量

### 调试模式 (问题排查)
```
1. aceflow_validate (检查问题) → 2. aceflow_stage (查看状态) → 3. 修复问题 → 4. 重新验证
```

## 🔧 故障排除

### 常见错误和解决方案

#### 1. 初始化相关错误
- **错误**: `"Directory already exists"`
- **原因**: 目标目录已存在项目文件
- **解决**: 使用不同的项目名称或清空目录
- **预防**: 初始化前检查目录状态

#### 2. 阶段推进相关错误
- **错误**: `"Current stage not completed"`
- **原因**: 当前阶段的工作尚未完成
- **解决**: 使用 `aceflow_validate` 检查完成条件
- **预防**: 每个阶段完成后进行验证

#### 3. 验证相关错误
- **错误**: `"Quality checks failed"`
- **原因**: 项目不符合质量标准
- **解决**: 查看详细报告并修复问题
- **预防**: 开发过程中定期验证

#### 4. 模板相关错误
- **错误**: `"Template not compatible"`
- **原因**: 当前项目状态与模板不兼容
- **解决**: 先完成当前阶段或重置项目状态
- **预防**: 在项目早期确定模板类型

### 调试技巧
1. **状态检查**: 使用 `aceflow_stage({"action": "status"})` 查看详细状态
2. **质量检查**: 使用 `aceflow_validate({"mode": "detailed", "report": true})` 获取详细报告
3. **日志分析**: 查看工具返回的错误信息和建议
4. **渐进式修复**: 一次解决一个问题，避免批量修改

### 性能优化建议
1. **批量操作**: 避免频繁调用相同工具
2. **缓存利用**: 相同参数的调用结果会被缓存
3. **并行处理**: 独立的验证和状态检查可以并行进行
4. **资源管理**: 大型项目建议使用 `complete` 模式的分阶段处理

## 📚 相关资源

- [AceFlow 官方文档](https://github.com/aceflow-ai/aceflow)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [项目模板说明](./README.md)

---

*本指南持续更新，如有问题请参考最新版本或提交 Issue。*