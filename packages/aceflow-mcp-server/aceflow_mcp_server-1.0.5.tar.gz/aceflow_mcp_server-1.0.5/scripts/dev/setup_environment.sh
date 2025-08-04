#!/bin/bash
# PyPI发布环境准备脚本

echo "🚀 AceFlow MCP Server - PyPI发布准备"
echo "=================================="

# 检查Python版本
echo "📋 检查Python环境..."
python --version
if [ $? -ne 0 ]; then
    echo "❌ Python未安装或不在PATH中"
    exit 1
fi

# 安装发布工具
echo "📦 安装发布工具..."
pip install --upgrade pip
pip install build twine wheel setuptools

# 检查必要工具
echo "🔍 验证工具安装..."
python -m build --help > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ build工具安装失败"
    exit 1
fi

twine --help > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ twine工具安装失败"
    exit 1
fi

echo "✅ 环境准备完成！"
echo ""
echo "📝 下一步操作："
echo "1. 注册PyPI账户: https://pypi.org/account/register/"
echo "2. 生成API Token: https://pypi.org/manage/account/token/"
echo "3. 配置认证信息 (运行 setup_pypi_auth.sh)"
echo "4. 构建和发布包 (运行 build_and_publish.sh)"