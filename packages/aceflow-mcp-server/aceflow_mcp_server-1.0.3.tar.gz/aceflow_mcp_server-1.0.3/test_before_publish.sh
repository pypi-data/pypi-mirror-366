#!/bin/bash
# 发布前测试脚本

echo "🧪 AceFlow MCP Server - 测试套件"
echo "==============================="

cd "$(dirname "$0")"

# 检查代码质量
echo "📊 检查代码质量..."

# 如果有 black，运行格式检查
if command -v black &> /dev/null; then
    echo "🎨 检查代码格式..."
    black --check aceflow_mcp_server/
fi

# 如果有 isort，检查导入排序
if command -v isort &> /dev/null; then
    echo "📚 检查导入排序..."
    isort --check-only aceflow_mcp_server/
fi

# 运行测试
echo "🧪 运行单元测试..."
python -m pytest tests/ -v --tb=short

if [ $? -eq 0 ]; then
    echo "✅ 所有测试通过！"
else
    echo "❌ 测试失败，请修复后重试"
    exit 1
fi

# 测试包导入
echo "📦 测试包导入..."
python -c "
try:
    from aceflow_mcp_server import AceFlowMCPServer
    from aceflow_mcp_server.tools import AceFlowTools
    from aceflow_mcp_server.resources import AceFlowResources
    from aceflow_mcp_server.prompts import AceFlowPrompts
    print('✅ 包导入成功')
except ImportError as e:
    print(f'❌ 包导入失败: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ 包准备就绪，可以发布！"
else
    echo "❌ 包导入测试失败"
    exit 1
fi