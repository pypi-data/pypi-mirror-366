#!/bin/bash
# 一键部署脚本 - 完整的PyPI发布流程

echo "🚀 AceFlow MCP Server - 一键发布到PyPI"
echo "===================================="

# 检查是否在正确目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

echo "📋 发布前检查清单："
echo "1. ✅ 是否已注册PyPI账户?"
echo "2. ✅ 是否已获取API Token?"
echo "3. ✅ 是否已测试代码功能?"
echo ""

read -p "确认以上都已完成，继续发布? (y/N): " proceed

if [[ ! $proceed =~ ^[Yy]$ ]]; then
    echo "❌ 发布取消"
    exit 0
fi

echo ""
echo "🚀 开始发布流程..."

# 1. 环境准备
echo "📦 步骤1: 准备环境..."
./setup_environment.sh
if [ $? -ne 0 ]; then
    echo "❌ 环境准备失败"
    exit 1
fi

# 2. 配置认证 (如果未配置)
if [ ! -f ~/.pypirc ]; then
    echo "🔐 步骤2: 配置PyPI认证..."
    ./setup_pypi_auth.sh
    if [ $? -ne 0 ]; then
        echo "❌ 认证配置失败"
        exit 1
    fi
else
    echo "✅ PyPI认证已配置"
fi

# 3. 运行测试
echo "🧪 步骤3: 运行测试..."
./test_before_publish.sh
if [ $? -ne 0 ]; then
    echo "❌ 测试失败，发布中止"
    exit 1
fi

# 4. 构建和发布
echo "📦 步骤4: 构建和发布..."
./build_and_publish.sh

echo ""
echo "🎉 发布流程完成！"
echo ""
echo "📝 后续步骤："
echo "1. 访问 https://pypi.org/project/aceflow-mcp-server/ 确认发布成功"
echo "2. 测试安装: pip install aceflow-mcp-server"
echo "3. 测试uvx: uvx aceflow-mcp-server"
echo "4. 更新文档和README中的安装说明"