#!/usr/bin/env python3
"""异步测试 MCP 服务器."""

import asyncio
from aceflow_mcp_server.server import mcp

async def test_mcp_async():
    """异步测试 MCP 服务器."""
    print("🔍 异步测试 AceFlow MCP Server")
    print("=" * 40)
    
    try:
        # 获取工具
        tools = await mcp.get_tools()
        print(f"🛠️  工具数量: {len(tools)}")
        for name, tool in tools.items():
            print(f"   - {name}: {tool}")
        
        # 获取资源
        resources = await mcp.get_resources()
        print(f"📚 资源数量: {len(resources)}")
        for name, resource in resources.items():
            print(f"   - {name}: {resource}")
        
        # 获取提示
        prompts = await mcp.get_prompts()
        print(f"💬 提示数量: {len(prompts)}")
        for name, prompt in prompts.items():
            print(f"   - {name}: {prompt}")
        
        print("\n✅ MCP 服务器异步检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_async())
    print(f"结果: {'成功' if success else '失败'}")