#!/bin/bash
# PyPI认证配置脚本

echo "🔐 配置PyPI认证"
echo "==============="

# 创建.pypirc配置文件
echo "📝 创建PyPI配置文件..."

read -p "请输入你的PyPI API Token (pypi-xxxxxxx): " api_token

if [ -z "$api_token" ]; then
    echo "❌ API Token不能为空"
    exit 1
fi

# 创建配置文件
cat > ~/.pypirc << EOF
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = $api_token
EOF

echo "✅ PyPI认证配置完成！"
echo "📁 配置文件位置: ~/.pypirc"
echo ""
echo "📝 API Token获取步骤："
echo "1. 登录 https://pypi.org/"
echo "2. 访问 Account Settings > API tokens"
echo "3. 创建新token，选择 'Entire account' 范围"
echo "4. 复制生成的token (格式: pypi-xxxxxx)"