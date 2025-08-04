#!/bin/bash
# 包构建和发布脚本

echo "🏗️ AceFlow MCP Server - 构建和发布"
echo "================================="

# 切换到项目目录
cd "$(dirname "$0")"

# 清理之前的构建
echo "🧹 清理之前的构建文件..."
rm -rf dist/ build/ *.egg-info/

# 运行测试
echo "🧪 运行测试套件..."
python -m pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "❌ 测试失败，请修复后重试"
    exit 1
fi

# 检查包配置
echo "🔍 验证包配置..."
python -m build --help > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ 构建工具未正确安装"
    exit 1
fi

# 构建包
echo "📦 构建Python包..."
python -m build

if [ $? -ne 0 ]; then
    echo "❌ 包构建失败"
    exit 1
fi

# 检查构建结果
echo "📋 检查构建文件..."
ls -la dist/

# 验证包
echo "🔍 验证包完整性..."
python -m twine check dist/*

if [ $? -ne 0 ]; then
    echo "❌ 包验证失败"
    exit 1
fi

# 询问是否发布
echo ""
echo "📦 构建完成！发现以下文件："
ls dist/

echo ""
read -p "确认发布到PyPI吗？(y/N): " confirm

if [[ $confirm =~ ^[Yy]$ ]]; then
    echo "🚀 发布到PyPI..."
    python -m twine upload dist/*
    
    if [ $? -eq 0 ]; then
        echo "✅ 发布成功！"
        echo ""
        echo "📝 安装测试："
        echo "pip install aceflow-mcp-server"
        echo ""
        echo "📝 或使用uvx："
        echo "uvx aceflow-mcp-server"
        echo ""
        echo "🔗 包页面: https://pypi.org/project/aceflow-mcp-server/"
    else
        echo "❌ 发布失败"
        exit 1
    fi
else
    echo "📦 构建完成，包已准备就绪在 dist/ 目录"
    echo "💡 手动发布命令: twine upload dist/*"
fi