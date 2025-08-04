#!/usr/bin/env python3
"""测试 MCP 工具注册的脚本"""

import asyncio
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

async def test_tool_registration():
    """测试工具注册"""
    try:
        from aceflow_mcp_server.server import mcp
        
        print("🔍 测试 MCP 工具注册...")
        print(f"MCP 实例类型: {type(mcp)}")
        
        # 获取注册的工具
        tools = await mcp.get_tools()
        print(f"✅ 注册的工具数量: {len(tools)}")
        
        for tool_name in tools:
            tool = await mcp.get_tool(tool_name)
            print(f"  - {tool_name}: {getattr(tool, 'description', 'No description')}")
        
        # 获取注册的资源
        resources = await mcp.get_resources()
        print(f"✅ 注册的资源数量: {len(resources)}")
        
        for resource_name in resources:
            resource = await mcp.get_resource(resource_name)
            print(f"  - {resource_name}: {getattr(resource, 'description', 'No description')}")
        
        # 获取注册的提示
        prompts = await mcp.get_prompts()
        print(f"✅ 注册的提示数量: {len(prompts)}")
        
        for prompt_name in prompts:
            prompt = await mcp.get_prompt(prompt_name)
            print(f"  - {prompt_name}: {getattr(prompt, 'description', 'No description')}")
            
        return len(tools) > 0
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_tool_registration())
    if success:
        print("🎉 工具注册测试成功！")
    else:
        print("💥 工具注册测试失败！")
        sys.exit(1)