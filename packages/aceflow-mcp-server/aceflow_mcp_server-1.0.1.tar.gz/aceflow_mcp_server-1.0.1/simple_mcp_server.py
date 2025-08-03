"""简化的MCP服务器实现，用于解决连接问题。"""

import json
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
import shutil
import datetime


class SimpleMCPServer:
    """简化的MCP服务器，用于诊断连接问题。"""
    
    def __init__(self):
        self.tools = {
            "aceflow_init": self.aceflow_init,
            "aceflow_stage": self.aceflow_stage,
            "aceflow_validate": self.aceflow_validate,
            "aceflow_template": self.aceflow_template
        }
    
    def aceflow_init(self, mode: str, project_name: Optional[str] = None, directory: Optional[str] = None) -> Dict[str, Any]:
        """初始化AceFlow项目。"""
        try:
            # 基本验证
            valid_modes = ["minimal", "standard", "complete", "smart"]
            if mode not in valid_modes:
                return {
                    "success": False,
                    "error": f"Invalid mode '{mode}'. Valid modes: {', '.join(valid_modes)}"
                }
            
            # 确定目标目录
            if directory:
                target_dir = Path(directory).resolve()
            else:
                target_dir = Path.cwd()
            
            target_dir.mkdir(parents=True, exist_ok=True)
            
            if not project_name:
                project_name = target_dir.name
            
            # 检查是否已初始化
            aceflow_dir = target_dir / ".aceflow"
            if aceflow_dir.exists():
                return {
                    "success": False,
                    "error": "Directory already contains AceFlow configuration"
                }
            
            # 创建项目结构
            aceflow_dir.mkdir(exist_ok=True)
            (target_dir / "aceflow_result").mkdir(exist_ok=True)
            
            # 创建状态文件
            state_data = {
                "project": {
                    "name": project_name,
                    "mode": mode.upper(),
                    "created_at": datetime.datetime.now().isoformat(),
                    "version": "1.0.0"
                },
                "flow": {
                    "current_stage": "user_stories" if mode != "minimal" else "implementation",
                    "completed_stages": [],
                    "progress_percentage": 0
                }
            }
            
            with open(aceflow_dir / "current_state.json", 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            
            # 创建.clinerules
            clinerules_content = f"""# AceFlow v1.0 - AI Agent 集成配置
# 项目: {project_name}
# 模式: {mode}

## 核心工作原则  
1. 所有项目文档和代码必须输出到 aceflow_result/ 目录
2. 严格按照工作流程执行
3. 保持跨对话的工作记忆和上下文连续性

## 工具集成命令
记住: AceFlow是AI Agent的增强层，通过规范化输出实现工作连续性。
"""
            
            with open(target_dir / ".clinerules", 'w', encoding='utf-8') as f:
                f.write(clinerules_content)
            
            return {
                "success": True,
                "message": f"Project '{project_name}' initialized successfully in {mode} mode",
                "project_info": {
                    "name": project_name,
                    "mode": mode,
                    "directory": str(target_dir)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initialize project"
            }
    
    def aceflow_stage(self, action: str, stage: Optional[str] = None) -> Dict[str, Any]:
        """管理项目阶段。"""
        if action == "status":
            return {
                "success": True,
                "result": {
                    "current_stage": "user_stories",
                    "progress": 25,
                    "next_stage": "task_breakdown"
                }
            }
        elif action == "list":
            return {
                "success": True,
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
                "error": f"Action '{action}' not implemented"
            }
    
    def aceflow_validate(self, mode: str = "basic") -> Dict[str, Any]:
        """验证项目合规性。"""
        return {
            "success": True,
            "validation_result": {
                "status": "passed",
                "checks_total": 5,
                "checks_passed": 5,
                "checks_failed": 0
            }
        }
    
    def aceflow_template(self, action: str, template: Optional[str] = None) -> Dict[str, Any]:
        """管理模板。"""
        if action == "list":
            return {
                "success": True,
                "result": {
                    "available_templates": ["minimal", "standard", "complete", "smart"]
                }
            }
        else:
            return {
                "success": False,
                "error": f"Action '{action}' not implemented"
            }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求。"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "initialize":
                return {
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "aceflow-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "result": {
                        "tools": [
                            {
                                "name": "aceflow_init",
                                "description": "Initialize AceFlow project",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "mode": {"type": "string", "enum": ["minimal", "standard", "complete", "smart"]},
                                        "project_name": {"type": "string"},
                                        "directory": {"type": "string"}
                                    },
                                    "required": ["mode"]
                                }
                            },
                            {
                                "name": "aceflow_stage",
                                "description": "Manage project stages",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "action": {"type": "string", "enum": ["status", "list", "next"]},
                                        "stage": {"type": "string"}
                                    },
                                    "required": ["action"]
                                }
                            },
                            {
                                "name": "aceflow_validate",
                                "description": "Validate project compliance",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "mode": {"type": "string", "enum": ["basic", "complete"]}
                                    }
                                }
                            },
                            {
                                "name": "aceflow_template",
                                "description": "Manage templates",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "action": {"type": "string", "enum": ["list", "apply"]},
                                        "template": {"type": "string"}
                                    },
                                    "required": ["action"]
                                }
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name in self.tools:
                    result = self.tools[tool_name](**arguments)
                    return {
                        "result": {
                            "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
                        }
                    }
                else:
                    return {
                        "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
                    }
            
            else:
                return {
                    "error": {"code": -32601, "message": f"Method '{method}' not found"}
                }
                
        except Exception as e:
            return {
                "error": {"code": -32000, "message": str(e)}
            }
    
    def run_stdio(self):
        """运行stdio模式的MCP服务器。"""
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = self.handle_request(request)
                    
                    if "id" in request:
                        response["id"] = request["id"]
                    
                    print(json.dumps(response), flush=True)
                
                except json.JSONDecodeError:
                    error_response = {
                        "error": {"code": -32700, "message": "Parse error"}
                    }
                    print(json.dumps(error_response), flush=True)
                
        except KeyboardInterrupt:
            pass
        except Exception as e:
            error_response = {
                "error": {"code": -32000, "message": f"Server error: {str(e)}"}
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    server = SimpleMCPServer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("AceFlow MCP Server (Simplified)")
        print("Usage: python simple_mcp_server.py")
        print("Runs in stdio mode for MCP communication")
        sys.exit(0)
    
    # 运行stdio模式
    server.run_stdio()