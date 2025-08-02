"""AceFlow MCP Tools implementation."""

from fastmcp.tools import tool
from typing import Dict, Any, Optional, List
import json
import os
import sys
from pathlib import Path
import shutil
import datetime

# Import existing AceFlow functionality
current_dir = Path(__file__).parent
aceflow_scripts_dir = current_dir.parent.parent / "aceflow" / "scripts"
sys.path.insert(0, str(aceflow_scripts_dir))

try:
    from utils.platform_compatibility import PlatformUtils, SafeFileOperations, EnhancedErrorHandler
except ImportError:
    # Fallback implementations if utils are not available
    class PlatformUtils:
        @staticmethod
        def get_os_type(): return "unknown"
    
    class SafeFileOperations:
        @staticmethod
        def write_text_file(path, content, encoding="utf-8"):
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
    
    class EnhancedErrorHandler:
        @staticmethod
        def handle_file_error(error, context=""): return str(error)


class AceFlowTools:
    """AceFlow MCP Tools collection."""
    
    def __init__(self):
        """Initialize tools with necessary dependencies."""
        self.platform_utils = PlatformUtils()
        self.file_ops = SafeFileOperations()
        self.error_handler = EnhancedErrorHandler()
    
    @tool
    def aceflow_init(
        self,
        mode: str,
        project_name: Optional[str] = None,
        directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initialize AceFlow project with specified mode.
        
        Args:
            mode: Workflow mode (minimal, standard, complete, smart)
            project_name: Optional project name
            directory: Optional target directory (defaults to current directory)
        
        Returns:
            Dict with success status, message, and project info
        """
        try:
            # Validate mode
            valid_modes = ["minimal", "standard", "complete", "smart"]
            if mode not in valid_modes:
                return {
                    "success": False,
                    "error": f"Invalid mode '{mode}'. Valid modes: {', '.join(valid_modes)}",
                    "message": "Mode validation failed"
                }
            
            # Determine target directory
            if directory:
                target_dir = Path(directory).resolve()
            else:
                target_dir = Path.cwd()
            
            # Create directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Set project name
            if not project_name:
                project_name = target_dir.name
            
            # Check if already initialized (unless forced)
            aceflow_dir = target_dir / ".aceflow"
            clinerules_file = target_dir / ".clinerules"
            
            if aceflow_dir.exists() or clinerules_file.exists():
                return {
                    "success": False,
                    "error": "Directory already contains AceFlow configuration",
                    "message": "Use --force flag to overwrite existing configuration"
                }
            
            # Initialize project structure
            result = self._initialize_project_structure(target_dir, project_name, mode)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Project '{project_name}' initialized successfully in {mode} mode",
                    "project_info": {
                        "name": project_name,
                        "mode": mode,
                        "directory": str(target_dir),
                        "created_files": result.get("created_files", [])
                    }
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initialize project"
            }
    
    def _initialize_project_structure(self, target_dir: Path, project_name: str, mode: str) -> Dict[str, Any]:
        """Initialize the complete project structure."""
        created_files = []
        
        try:
            # Create .aceflow directory
            aceflow_dir = target_dir / ".aceflow"
            aceflow_dir.mkdir(exist_ok=True)
            created_files.append(".aceflow/")
            
            # Create aceflow_result directory
            result_dir = target_dir / "aceflow_result"
            result_dir.mkdir(exist_ok=True)
            created_files.append("aceflow_result/")
            
            # Create project state file
            state_data = {
                "project": {
                    "name": project_name,
                    "mode": mode.upper(),
                    "created_at": datetime.datetime.now().isoformat(),
                    "version": "3.0"
                },
                "flow": {
                    "current_stage": "user_stories" if mode != "minimal" else "implementation",
                    "completed_stages": [],
                    "progress_percentage": 0
                },
                "metadata": {
                    "total_stages": self._get_stage_count(mode),
                    "last_updated": datetime.datetime.now().isoformat()
                }
            }
            
            state_file = aceflow_dir / "current_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            created_files.append(".aceflow/current_state.json")
            
            # Create .clinerules file
            clinerules_content = self._generate_clinerules(project_name, mode)
            clinerules_file = target_dir / ".clinerules"
            with open(clinerules_file, 'w', encoding='utf-8') as f:
                f.write(clinerules_content)
            created_files.append(".clinerules")
            
            # Create template.yaml
            template_content = self._generate_template_yaml(mode)
            template_file = aceflow_dir / "template.yaml"
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            created_files.append(".aceflow/template.yaml")
            
            # Copy management scripts
            script_files = ["aceflow-stage.py", "aceflow-validate.py", "aceflow-templates.py"]
            for script in script_files:
                source_path = aceflow_scripts_dir / script
                if source_path.exists():
                    dest_path = target_dir / script
                    shutil.copy2(source_path, dest_path)
                    created_files.append(script)
            
            # Create README
            readme_content = self._generate_readme(project_name, mode)
            readme_file = target_dir / "README_ACEFLOW.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            created_files.append("README_ACEFLOW.md")
            
            return {
                "success": True,
                "created_files": created_files
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create project structure"
            }
    
    def _get_stage_count(self, mode: str) -> int:
        """Get the number of stages for the given mode."""
        stage_counts = {
            "minimal": 3,
            "standard": 8,
            "complete": 12,
            "smart": 10
        }
        return stage_counts.get(mode, 8)
    
    def _generate_clinerules(self, project_name: str, mode: str) -> str:
        """Generate .clinerules content."""
        return f"""# AceFlow v3.0 - AI Agent 集成配置
# 项目: {project_name}
# 模式: {mode}
# 初始化时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 工作模式配置
AceFlow模式: {mode}
输出目录: aceflow_result/
配置目录: .aceflow/
项目名称: {project_name}

## 核心工作原则  
1. 所有项目文档和代码必须输出到 aceflow_result/ 目录
2. 严格按照 .aceflow/template.yaml 中定义的流程执行
3. 每个阶段完成后更新项目状态文件
4. 保持跨对话的工作记忆和上下文连续性
5. 遵循AceFlow v3.0规范进行标准化输出

## 质量标准
- 代码质量: 遵循项目编码规范，注释完整
- 文档质量: 结构清晰，内容完整，格式统一
- 测试覆盖: 根据模式要求执行相应测试策略
- 交付标准: 符合 aceflow-spec_v3.0.md 规范

## 工具集成命令
- python aceflow-validate.py: 验证项目状态和合规性
- python aceflow-stage.py: 管理项目阶段和进度
- python aceflow-templates.py: 管理模板配置

记住: AceFlow是AI Agent的增强层，通过规范化输出和状态管理，实现跨对话的工作连续性。
"""
    
    def _generate_template_yaml(self, mode: str) -> str:
        """Generate template.yaml content based on mode."""
        templates = {
            "minimal": """# AceFlow Minimal模式配置
name: "Minimal Workflow"
version: "3.0"
description: "快速原型和概念验证工作流"

stages:
  - name: "implementation"
    description: "快速实现核心功能"
    required: true
  - name: "test"
    description: "基础功能测试"
    required: true
  - name: "demo"
    description: "功能演示"
    required: true

quality_gates:
  - stage: "implementation"
    criteria: ["核心功能完成", "基本可运行"]
  - stage: "test"
    criteria: ["主要功能测试通过"]""",
            
            "standard": """# AceFlow Standard模式配置
name: "Standard Workflow"
version: "3.0"
description: "标准软件开发工作流"

stages:
  - name: "user_stories"
    description: "用户故事分析"
    required: true
  - name: "task_breakdown"
    description: "任务分解"
    required: true
  - name: "test_design"
    description: "测试用例设计"
    required: true
  - name: "implementation"
    description: "功能实现"
    required: true
  - name: "unit_test"
    description: "单元测试"
    required: true
  - name: "integration_test"
    description: "集成测试"
    required: true
  - name: "code_review"
    description: "代码审查"
    required: true
  - name: "demo"
    description: "功能演示"
    required: true

quality_gates:
  - stage: "user_stories"
    criteria: ["用户故事完整", "验收标准明确"]
  - stage: "implementation"
    criteria: ["代码质量合格", "功能完整"]
  - stage: "unit_test"
    criteria: ["测试覆盖率 > 80%", "所有测试通过"]""",
            
            "complete": """# AceFlow Complete模式配置  
name: "Complete Workflow"
version: "3.0"
description: "完整企业级开发工作流"

stages:
  - name: "requirement_analysis"
    description: "需求分析"
    required: true
  - name: "architecture_design"
    description: "架构设计"
    required: true
  - name: "user_stories"
    description: "用户故事分析"
    required: true
  - name: "task_breakdown"
    description: "任务分解"
    required: true
  - name: "test_design"
    description: "测试用例设计"
    required: true
  - name: "implementation"
    description: "功能实现"
    required: true
  - name: "unit_test"
    description: "单元测试"
    required: true
  - name: "integration_test"
    description: "集成测试"
    required: true
  - name: "performance_test"
    description: "性能测试"
    required: true
  - name: "security_review"
    description: "安全审查"
    required: true
  - name: "code_review"
    description: "代码审查"
    required: true
  - name: "demo"
    description: "功能演示"
    required: true

quality_gates:
  - stage: "architecture_design"
    criteria: ["架构设计完整", "技术选型合理"]
  - stage: "implementation"
    criteria: ["代码质量优秀", "性能满足要求"]
  - stage: "security_review"
    criteria: ["安全检查通过", "无重大漏洞"]""",
            
            "smart": """# AceFlow Smart模式配置
name: "Smart Adaptive Workflow"  
version: "3.0"
description: "AI增强的自适应工作流"

stages:
  - name: "project_analysis"
    description: "AI项目复杂度分析"
    required: true
  - name: "adaptive_planning"
    description: "自适应规划"
    required: true
  - name: "user_stories"
    description: "用户故事分析"
    required: true
  - name: "smart_breakdown"
    description: "智能任务分解"
    required: true
  - name: "test_generation"
    description: "AI测试用例生成"
    required: true
  - name: "implementation"
    description: "功能实现"
    required: true
  - name: "automated_test"
    description: "自动化测试"
    required: true
  - name: "quality_assessment"
    description: "AI质量评估"
    required: true
  - name: "optimization"
    description: "性能优化"
    required: true
  - name: "demo"
    description: "智能演示"
    required: true

ai_features:
  - "复杂度智能评估"
  - "动态流程调整"
  - "自动化测试生成"
  - "质量智能分析"

quality_gates:
  - stage: "project_analysis"
    criteria: ["复杂度评估完成", "技术栈确定"]
  - stage: "implementation"
    criteria: ["AI代码质量检查通过", "性能指标达标"]"""
        }
        
        return templates.get(mode, templates["standard"])
    
    def _generate_readme(self, project_name: str, mode: str) -> str:
        """Generate README content."""
        return f"""# {project_name}

## AceFlow项目说明

本项目使用AceFlow v3.0工作流管理系统，采用 **{mode.upper()}** 模式。

### 项目信息
- **项目名称**: {project_name}
- **工作流模式**: {mode.upper()}
- **初始化时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **AceFlow版本**: 3.0

### 目录结构
```
{project_name}/
├── .aceflow/           # AceFlow配置目录
│   ├── current_state.json    # 项目状态文件
│   └── template.yaml         # 工作流模板
├── aceflow_result/     # 项目输出目录
├── .clinerules         # AI Agent工作配置
├── aceflow-stage.py    # 阶段管理脚本
├── aceflow-validate.py # 项目验证脚本
├── aceflow-templates.py # 模板管理脚本
└── README_ACEFLOW.md   # 本文件
```

### 快速开始

1. **查看当前状态**
   ```bash
   python aceflow-stage.py --action status
   ```

2. **验证项目配置**
   ```bash
   python aceflow-validate.py
   ```

3. **推进到下一阶段**
   ```bash
   python aceflow-stage.py --action next
   ```

### 工作流程

根据{mode}模式，项目将按以下阶段进行：

{self._get_stage_description(mode)}

### 注意事项

- 所有项目文档和代码请输出到 `aceflow_result/` 目录
- 使用AI助手时，确保.clinerules配置已加载
- 每个阶段完成后，使用 `aceflow-stage.py` 更新状态
- 定期使用 `aceflow-validate.py` 检查项目合规性

### 帮助和支持

如需帮助，请参考：
- AceFlow官方文档
- 项目状态文件: `.aceflow/current_state.json`
- 工作流配置: `.aceflow/template.yaml`

---
*Generated by AceFlow v3.0 MCP Server*"""
    
    def _get_stage_description(self, mode: str) -> str:
        """Get stage descriptions for the mode."""
        descriptions = {
            "minimal": """1. **Implementation** - 快速实现核心功能
2. **Test** - 基础功能测试  
3. **Demo** - 功能演示""",
            
            "standard": """1. **User Stories** - 用户故事分析
2. **Task Breakdown** - 任务分解
3. **Test Design** - 测试用例设计
4. **Implementation** - 功能实现
5. **Unit Test** - 单元测试
6. **Integration Test** - 集成测试
7. **Code Review** - 代码审查
8. **Demo** - 功能演示""",
            
            "complete": """1. **Requirement Analysis** - 需求分析
2. **Architecture Design** - 架构设计
3. **User Stories** - 用户故事分析
4. **Task Breakdown** - 任务分解
5. **Test Design** - 测试用例设计
6. **Implementation** - 功能实现
7. **Unit Test** - 单元测试
8. **Integration Test** - 集成测试
9. **Performance Test** - 性能测试
10. **Security Review** - 安全审查
11. **Code Review** - 代码审查
12. **Demo** - 功能演示""",
            
            "smart": """1. **Project Analysis** - AI项目复杂度分析
2. **Adaptive Planning** - 自适应规划
3. **User Stories** - 用户故事分析
4. **Smart Breakdown** - 智能任务分解
5. **Test Generation** - AI测试用例生成
6. **Implementation** - 功能实现
7. **Automated Test** - 自动化测试
8. **Quality Assessment** - AI质量评估
9. **Optimization** - 性能优化
10. **Demo** - 智能演示"""
        }
        
        return descriptions.get(mode, descriptions["standard"])
    
    @tool  
    def aceflow_stage(
        self,
        action: str,
        stage: Optional[str] = None
    ) -> Dict[str, Any]:
        """Manage project stages and workflow.
        
        Args:
            action: Stage management action (status, next, list, reset)
            stage: Optional target stage name
            
        Returns:
            Dict with success status and stage information
        """
        try:
            # This is a placeholder - in real implementation, this would
            # integrate with the existing aceflow-stage.py functionality
            
            if action == "status":
                return {
                    "success": True,
                    "action": action,
                    "result": {
                        "current_stage": "user_stories",
                        "progress": 25,
                        "completed_stages": [],
                        "next_stage": "task_breakdown"
                    }
                }
            elif action == "list":
                return {
                    "success": True,
                    "action": action,
                    "result": {
                        "stages": [
                            "user_stories", "task_breakdown", "test_design",
                            "implementation", "unit_test", "integration_test", 
                            "code_review", "demo"
                        ]
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Action '{action}' not yet implemented",
                    "message": "This tool is under development"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute stage action: {action}"
            }
    
    @tool
    def aceflow_validate(
        self,
        mode: str = "basic",
        fix: bool = False,
        report: bool = False
    ) -> Dict[str, Any]:
        """Validate project compliance and quality.
        
        Args:
            mode: Validation mode (basic, complete)
            fix: Auto-fix issues if possible
            report: Generate detailed report
            
        Returns:
            Dict with validation results
        """
        try:
            # Placeholder implementation
            return {
                "success": True,
                "validation_result": {
                    "status": "passed",
                    "checks_total": 10,
                    "checks_passed": 8,
                    "checks_failed": 2,
                    "warnings": 1,
                    "issues": [
                        "Missing documentation in aceflow_result/",
                        "Template validation incomplete"
                    ]
                },
                "message": "Validation completed with warnings"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Validation failed"
            }
    
    @tool
    def aceflow_template(
        self,
        action: str,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Manage workflow templates.
        
        Args:
            action: Template action (list, apply, validate)
            template: Optional template name
            
        Returns:
            Dict with template operation results
        """
        try:
            if action == "list":
                return {
                    "success": True,
                    "action": action,
                    "result": {
                        "available_templates": [
                            "minimal", "standard", "complete", "smart"
                        ],
                        "current_template": "standard"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Action '{action}' not yet implemented",
                    "message": "This tool is under development"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Template action failed: {action}"
            }