#!/bin/bash
# 发布前测试脚本

echo "🧪 运行发布前测试..."
echo "=================="

# 切换到项目根目录
cd "$(dirname "$0")/../.." || exit 1

# 运行单元测试
echo "🧪 运行单元测试..."
python -m pytest tests/

if [ $? -ne 0 ]; then
    echo "❌ 单元测试失败"
    exit 1
fi

# 构建测试包
echo "📦 构建测试包..."
python -m build --sdist --wheel

if [ $? -ne 0 ]; then
    echo "❌ 测试包构建失败"
    exit 1
fi

# 验证包
echo "🔍 验证包..."
twine check dist/*

if [ $? -ne 0 ]; then
    echo "❌ 包验证失败"
    exit 1
fi

# 检查版本号
echo "🔢 检查版本号..."
VERSION=$(grep -m 1 "version" pyproject.toml | cut -d'"' -f2)
echo "当前版本: $VERSION"

# 检查是否已存在该版本
echo "🔍 检查PyPI上是否已存在该版本..."
pip install aceflow-mcp-server==$VERSION &> /dev/null
if [ $? -eq 0 ]; then
    echo "⚠️ 警告: 版本 $VERSION 已存在于PyPI上"
    echo "请更新版本号后再发布"
    exit 1
else
    echo "✅ 版本号检查通过"
fi

echo "✅ 所有测试通过！"