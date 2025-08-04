#!/usr/bin/env python3
"""测试完整的 MCP 协议交互"""

import json
import sys
import subprocess
import asyncio
import os

def test_mcp_protocol():
    """测试 MCP 协议交互"""
    print("🔍 测试 MCP 协议交互...", file=sys.stderr)
    
    # 启动 MCP 服务器进程
    cmd = [
        sys.executable, "-m", "aceflow_mcp_server.server", 
        "--transport", "stdio", "--log-level", "ERROR"
    ]
    
    print(f"启动命令: {' '.join(cmd)}", file=sys.stderr)
    
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        # 发送初始化请求
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
        
        print(f"发送: {json.dumps(init_request)}", file=sys.stderr)
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # 读取响应
        response_line = process.stdout.readline()
        print(f"收到: {response_line.strip()}", file=sys.stderr)
        
        if response_line:
            try:
                response = json.loads(response_line)
                print(f"解析响应: {response}", file=sys.stderr)
            except json.JSONDecodeError as e:
                print(f"JSON 解析错误: {e}", file=sys.stderr)
        
        # 发送工具列表请求
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print(f"发送: {json.dumps(tools_request)}", file=sys.stderr)
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        # 读取工具列表响应
        tools_response_line = process.stdout.readline()
        print(f"工具列表响应: {tools_response_line.strip()}", file=sys.stderr)
        
        if tools_response_line:
            try:
                tools_response = json.loads(tools_response_line)
                print(f"工具列表: {tools_response}", file=sys.stderr)
                
                # 检查是否有工具
                if 'result' in tools_response and 'tools' in tools_response['result']:
                    tools = tools_response['result']['tools']
                    print(f"✅ 找到 {len(tools)} 个工具:", file=sys.stderr)
                    for tool in tools:
                        print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}", file=sys.stderr)
                    return len(tools) > 0
                else:
                    print("❌ 响应中没有找到工具", file=sys.stderr)
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"工具列表 JSON 解析错误: {e}", file=sys.stderr)
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}", file=sys.stderr)
        return False
    finally:
        if 'process' in locals():
            process.terminate()
            process.wait()

if __name__ == "__main__":
    success = test_mcp_protocol()
    if success:
        print("🎉 MCP 协议测试成功！", file=sys.stderr)
    else:
        print("💥 MCP 协议测试失败！", file=sys.stderr)
        sys.exit(1)