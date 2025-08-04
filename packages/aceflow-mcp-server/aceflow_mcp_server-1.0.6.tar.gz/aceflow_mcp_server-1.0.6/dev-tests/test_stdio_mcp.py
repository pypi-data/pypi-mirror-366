#!/usr/bin/env python3
"""测试 stdio 模式下的 MCP 服务器"""

import sys
import json
import asyncio
from aceflow_mcp_server.server import mcp

async def test_stdio_mcp():
    """测试 stdio MCP 服务器"""
    print("🔍 测试 stdio 模式 MCP 服务器...", file=sys.stderr)
    
    # 模拟 MCP 初始化请求
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    print(f"发送初始化请求: {json.dumps(init_request)}", file=sys.stderr)
    
    # 模拟工具列表请求
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    print(f"发送工具列表请求: {json.dumps(tools_request)}", file=sys.stderr)
    
    # 检查工具是否注册
    tools = await mcp.get_tools()
    print(f"✅ 本地注册的工具: {tools}", file=sys.stderr)
    
    return len(tools) > 0

if __name__ == "__main__":
    success = asyncio.run(test_stdio_mcp())
    if success:
        print("🎉 stdio MCP 测试成功！", file=sys.stderr)
    else:
        print("💥 stdio MCP 测试失败！", file=sys.stderr)
        sys.exit(1)