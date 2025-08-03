#!/usr/bin/env python3
"""Check if AceFlow MCP Server is ready for PyPI publication."""

import sys
import subprocess
import json
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def check_file_exists(file_path, description):
    """Check if a file exists."""
    print(f"🔍 {description}...")
    if Path(file_path).exists():
        print(f"✅ {description} - EXISTS")
        return True
    else:
        print(f"❌ {description} - MISSING")
        return False


def main():
    """Main check function."""
    print("🚀 AceFlow MCP Server - PyPI 发布准备检查")
    print("=" * 50)
    
    checks = []
    
    # 1. Check required files
    print("\n📁 检查必需文件...")
    checks.append(check_file_exists("pyproject.toml", "pyproject.toml 配置文件"))
    checks.append(check_file_exists("README.md", "README.md 文档"))
    checks.append(check_file_exists("LICENSE", "LICENSE 许可证文件"))
    checks.append(check_file_exists("aceflow_mcp_server/__init__.py", "包初始化文件"))
    checks.append(check_file_exists("aceflow_mcp_server/server.py", "服务器主文件"))
    checks.append(check_file_exists("aceflow_mcp_server/tools.py", "工具模块"))
    checks.append(check_file_exists("aceflow_mcp_server/resources.py", "资源模块"))
    checks.append(check_file_exists("aceflow_mcp_server/prompts.py", "提示模块"))
    
    # 2. Check tests
    print("\n🧪 检查测试...")
    checks.append(run_command("python -m pytest tests/ -v", "运行测试套件"))
    
    # 3. Check test coverage
    print("\n📊 检查测试覆盖率...")
    coverage_result = subprocess.run(
        "python -m pytest tests/ --cov=aceflow_mcp_server --cov-report=json",
        shell=True, capture_output=True, text=True
    )
    
    if coverage_result.returncode == 0:
        try:
            with open("coverage.json", "r") as f:
                coverage_data = json.load(f)
            
            total_coverage = coverage_data["totals"]["percent_covered"]
            if total_coverage >= 80:
                print(f"✅ 测试覆盖率 - {total_coverage:.1f}% (>= 80%)")
                checks.append(True)
            else:
                print(f"❌ 测试覆盖率 - {total_coverage:.1f}% (< 80%)")
                checks.append(False)
        except Exception as e:
            print(f"❌ 无法读取覆盖率数据: {e}")
            checks.append(False)
    else:
        print("❌ 覆盖率检查失败")
        checks.append(False)
    
    # 4. Check package import
    print("\n📦 检查包导入...")
    checks.append(run_command(
        "python -c \"from aceflow_mcp_server import AceFlowMCPServer; print('导入成功')\"",
        "包导入测试"
    ))
    
    # 5. Check build tools
    print("\n🛠️ 检查构建工具...")
    checks.append(run_command("python -m build --help", "build 工具"))
    checks.append(run_command("python -m twine --help", "twine 工具"))
    
    # 6. Build package
    print("\n📦 构建包...")
    checks.append(run_command("python -m build", "包构建"))
    
    # 7. Validate package
    print("\n✅ 验证包...")
    checks.append(run_command("python -m twine check dist/*", "包验证"))
    
    # 8. Check MCP tools
    print("\n🔧 检查 MCP 工具...")
    test_tools_cmd = """
python -c "
from aceflow_mcp_server.tools import AceFlowTools
tools = AceFlowTools()
result = tools.aceflow_init.fn(tools, 'minimal', 'test-project')
print('MCP 工具测试:', 'PASSED' if result['success'] else 'FAILED')
"
"""
    checks.append(run_command(test_tools_cmd, "MCP 工具功能测试"))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 检查结果汇总")
    print("=" * 50)
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {total - passed}")
    print(f"📊 成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有检查通过！包已准备好发布到 PyPI。")
        print("\n📝 下一步操作:")
        print("1. 运行 ./deploy_to_pypi.sh 进行一键发布")
        print("2. 或手动运行 python -m twine upload dist/*")
        return 0
    else:
        print(f"\n⚠️ 有 {total - passed} 项检查失败，请修复后重试。")
        return 1


if __name__ == "__main__":
    sys.exit(main())