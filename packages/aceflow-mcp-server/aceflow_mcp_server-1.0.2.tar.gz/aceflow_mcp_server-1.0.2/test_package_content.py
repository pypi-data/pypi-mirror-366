#!/usr/bin/env python3
"""Test script to verify package content."""

import sys
import inspect
from pathlib import Path

def test_package_content():
    """Test the package content to ensure no decorators remain."""
    print("🔍 Testing package content...")
    
    try:
        # Import the package
        from aceflow_mcp_server.tools import AceFlowTools
        from aceflow_mcp_server.server import main
        
        print("✅ Package imports successfully")
        
        # Check tools class
        tools = AceFlowTools()
        print(f"✅ AceFlowTools instantiated: {tools}")
        
        # Check if methods exist and are callable
        methods = ['aceflow_init', 'aceflow_stage', 'aceflow_validate', 'aceflow_template']
        for method_name in methods:
            if hasattr(tools, method_name):
                method = getattr(tools, method_name)
                if callable(method):
                    print(f"✅ {method_name} is callable")
                else:
                    print(f"❌ {method_name} is not callable")
            else:
                print(f"❌ {method_name} not found")
        
        # Check server main function
        if callable(main):
            print("✅ main function is callable")
        else:
            print("❌ main function is not callable")
        
        # Check source file for decorators
        import aceflow_mcp_server.tools as tools_module
        source_file = inspect.getfile(tools_module)
        print(f"📁 Tools source file: {source_file}")
        
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '@tool' in content or '@mcp.tool' in content:
            print("❌ Found @tool decorators in tools.py")
            # Find line numbers
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if '@tool' in line or '@mcp.tool' in line:
                    print(f"   Line {i}: {line.strip()}")
        else:
            print("✅ No @tool decorators found in tools.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing package: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_package_content()
    sys.exit(0 if success else 1)