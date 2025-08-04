#!/bin/bash
# MCP服务器诊断脚本

echo "🔍 AceFlow MCP Server 诊断"
echo "========================="

# 1. 检查uvx安装
echo "📦 检查uvx安装..."
if command -v uvx &> /dev/null; then
    echo "✅ uvx已安装: $(uvx --version)"
else
    echo "❌ uvx未安装"
    echo "安装命令: pip install uvx"
    exit 1
fi

# 2. 检查Python环境
echo "🐍 检查Python环境..."
python3 --version
which python3

# 3. 测试包安装
echo "📦 检查AceFlow MCP Server包..."
if uvx run aceflow-mcp-server --help &> /dev/null; then
    echo "✅ 包可正常运行"
else
    echo "❌ 包运行失败，尝试安装..."
    uvx install aceflow-mcp-server
fi

# 4. 测试服务器启动
echo "🚀 测试服务器启动..."
timeout 10s uvx run aceflow-mcp-server --host localhost --port 8001 &
SERVER_PID=$!
sleep 3

if ps -p $SERVER_PID > /dev/null; then
    echo "✅ 服务器启动成功"
    kill $SERVER_PID
else
    echo "❌ 服务器启动失败"
fi

# 5. 检查端口占用
echo "🔌 检查端口占用..."
netstat -tulpn | grep :8000 || echo "端口8000未被占用"

echo ""
echo "📝 诊断完成！"