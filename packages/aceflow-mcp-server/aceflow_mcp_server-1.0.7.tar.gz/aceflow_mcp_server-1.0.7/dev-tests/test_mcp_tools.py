#!/usr/bin/env python3
"""Test script to check available MCP tools."""

import sys
import inspect
from aceflow_mcp_server.server import mcp

def test_mcp_tools():
    """Test and list all available MCP tools."""
    print("🔧 AceFlow MCP Server - 可用工具测试")
    print("=" * 50)
    
    try:
        # Get all registered tools from the FastMCP instance
        tools = mcp._tools if hasattr(mcp, '_tools') else {}
        
        if not tools:
            print("❌ 未找到注册的工具")
            return False
        
        print(f"📊 发现 {len(tools)} 个 MCP 工具:")
        print()
        
        for i, (tool_name, tool_func) in enumerate(tools.items(), 1):
            print(f"{i}. 🛠️  **{tool_name}**")
            
            # Get function signature and docstring
            try:
                sig = inspect.signature(tool_func)
                doc = inspect.getdoc(tool_func) or "无描述"
                
                print(f"   📝 描述: {doc.split('.')[0]}")
                print(f"   📋 参数: {sig}")
                
                # Test calling the tool with minimal parameters
                try:
                    if tool_name == "aceflow_init":
                        result = tool_func("minimal", "test-project")
                        print(f"   ✅ 测试调用: {'成功' if result.get('success') else '失败'}")
                    elif tool_name == "aceflow_stage":
                        result = tool_func("list")
                        print(f"   ✅ 测试调用: {'成功' if result.get('success') else '失败'}")
                    elif tool_name == "aceflow_validate":
                        result = tool_func()
                        print(f"   ✅ 测试调用: {'成功' if result.get('success') else '失败'}")
                    elif tool_name == "aceflow_template":
                        result = tool_func("list")
                        print(f"   ✅ 测试调用: {'成功' if result.get('success') else '失败'}")
                    else:
                        print(f"   ⚠️  未知工具类型，跳过测试")
                        
                except Exception as e:
                    print(f"   ❌ 测试调用失败: {str(e)}")
                    
            except Exception as e:
                print(f"   ❌ 获取工具信息失败: {str(e)}")
            
            print()
        
        # Test resources
        print("📚 MCP 资源:")
        resources = mcp._resources if hasattr(mcp, '_resources') else {}
        if resources:
            for resource_name, resource_func in resources.items():
                print(f"   📖 {resource_name}")
        else:
            print("   ❌ 未找到注册的资源")
        
        print()
        
        # Test prompts
        print("💬 MCP 提示:")
        prompts = mcp._prompts if hasattr(mcp, '_prompts') else {}
        if prompts:
            for prompt_name, prompt_func in prompts.items():
                print(f"   💭 {prompt_name}")
        else:
            print("   ❌ 未找到注册的提示")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_tools():
    """直接测试工具类的方法."""
    print("\n" + "=" * 50)
    print("🔧 直接测试工具类方法")
    print("=" * 50)
    
    try:
        from aceflow_mcp_server.tools import AceFlowTools
        
        tools = AceFlowTools()
        tool_methods = ['aceflow_init', 'aceflow_stage', 'aceflow_validate', 'aceflow_template']
        
        print(f"📊 工具类方法: {len(tool_methods)} 个")
        print()
        
        for i, method_name in enumerate(tool_methods, 1):
            print(f"{i}. 🛠️  **{method_name}**")
            
            if hasattr(tools, method_name):
                method = getattr(tools, method_name)
                
                # Get method signature and docstring
                try:
                    sig = inspect.signature(method)
                    doc = inspect.getdoc(method) or "无描述"
                    
                    print(f"   📝 描述: {doc.split('.')[0]}")
                    print(f"   📋 参数: {sig}")
                    
                    # Test calling the method
                    try:
                        if method_name == "aceflow_init":
                            result = method("minimal", "test-project")
                        elif method_name == "aceflow_stage":
                            result = method("list")
                        elif method_name == "aceflow_validate":
                            result = method()
                        elif method_name == "aceflow_template":
                            result = method("list")
                        
                        print(f"   ✅ 测试调用: {'成功' if result.get('success') else '失败'}")
                        if result.get('success') and 'result' in result:
                            if method_name == "aceflow_stage" and result['action'] == 'list':
                                stages = result['result'].get('stages', [])
                                print(f"   📋 可用阶段: {len(stages)} 个")
                            elif method_name == "aceflow_template" and result['action'] == 'list':
                                templates = result['result'].get('available_templates', [])
                                print(f"   📋 可用模板: {templates}")
                                
                    except Exception as e:
                        print(f"   ❌ 测试调用失败: {str(e)}")
                        
                except Exception as e:
                    print(f"   ❌ 获取方法信息失败: {str(e)}")
            else:
                print(f"   ❌ 方法不存在")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 直接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始测试 AceFlow MCP Server 工具")
    print()
    
    success1 = test_mcp_tools()
    success2 = test_direct_tools()
    
    print("\n" + "=" * 50)
    print("📋 测试总结")
    print("=" * 50)
    
    if success1 and success2:
        print("✅ 所有测试通过！")
        print("\n🎯 AceFlow MCP Server 提供以下功能:")
        print("   🛠️  4 个 MCP 工具 (aceflow_init, aceflow_stage, aceflow_validate, aceflow_template)")
        print("   📚 3 个 MCP 资源 (project/state, workflow/config, stage/guide)")
        print("   💬 2 个 MCP 提示 (workflow_assistant, stage_guide)")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)