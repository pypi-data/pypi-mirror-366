#!/usr/bin/env python3
"""测试 MCP 服务器启动."""

import sys
import asyncio
from aceflow_mcp_server.server import mcp

async def test_mcp_server():
    """测试 MCP 服务器."""
    print("🔍 测试 AceFlow MCP Server")
    print("=" * 40)
    
    try:
        # 检查 FastMCP 实例
        print(f"📊 MCP 实例: {mcp}")
        print(f"📊 MCP 类型: {type(mcp)}")
        
        # 检查注册的工具
        if hasattr(mcp, '_tools'):
            tools = mcp._tools
            print(f"🛠️  注册的工具数量: {len(tools)}")
            for name in tools.keys():
                print(f"   - {name}")
        else:
            print("❌ 未找到工具注册信息")
        
        # 检查注册的资源
        if hasattr(mcp, '_resources'):
            resources = mcp._resources
            print(f"📚 注册的资源数量: {len(resources)}")
            for name in resources.keys():
                print(f"   - {name}")
        else:
            print("❌ 未找到资源注册信息")
        
        # 检查注册的提示
        if hasattr(mcp, '_prompts'):
            prompts = mcp._prompts
            print(f"💬 注册的提示数量: {len(prompts)}")
            for name in prompts.keys():
                print(f"   - {name}")
        else:
            print("❌ 未找到提示注册信息")
        
        print("\n✅ MCP 服务器配置检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)