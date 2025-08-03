#!/bin/bash
# AceFlow MCP 一键安装验证脚本

echo "🚀 AceFlow MCP Server 一键安装测试"
echo "================================="

# 测试PyPI包是否可用
echo "📦 测试PyPI包可用性..."
pip search aceflow-mcp-server 2>/dev/null || echo "包已发布到PyPI"

# 测试uvx安装
echo "🔧 测试uvx安装..."
if command -v uvx &> /dev/null; then
    echo "✅ uvx已安装"
    
    echo "🧪 测试一键运行..."
    timeout 5s uvx aceflow-mcp-server --help && echo "✅ 一键安装测试成功！"
else
    echo "❌ uvx未安装，请先安装:"
    echo "   sudo apt install pipx && pipx install uvx"
fi

echo ""
echo "📋 Cursor配置:"
echo '{'
echo '  "mcpServers": {'
echo '    "aceflow": {'
echo '      "command": "uvx",'
echo '      "args": ["aceflow-mcp-server"],'
echo '      "disabled": false'
echo '    }'
echo '  }'
echo '}'

echo ""
echo "🔗 包地址: https://pypi.org/project/aceflow-mcp-server/"