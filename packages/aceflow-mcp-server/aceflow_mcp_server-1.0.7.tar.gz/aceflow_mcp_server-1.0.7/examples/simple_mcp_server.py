#!/usr/bin/env python3
"""简单的 MCP 服务器用于测试"""

import asyncio
import json
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from typing import Any, Sequence

# 创建服务器实例
server = Server("aceflow-simple")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="aceflow_test",
            description="Test AceFlow tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Test message"
                    }
                },
                "required": ["message"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """调用工具"""
    if name == "aceflow_test":
        message = arguments.get("message", "Hello from AceFlow!")
        return [TextContent(type="text", text=f"AceFlow says: {message}")]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """主函数"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())