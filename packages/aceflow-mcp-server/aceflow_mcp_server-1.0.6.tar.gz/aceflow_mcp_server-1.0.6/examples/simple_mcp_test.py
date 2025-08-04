#!/usr/bin/env python3
"""简单的 MCP 工具测试."""

def test_aceflow_tools():
    """测试 AceFlow MCP 工具."""
    print("🔧 AceFlow MCP Server - 工具功能测试")
    print("=" * 50)
    
    from aceflow_mcp_server.tools import AceFlowTools
    from aceflow_mcp_server.resources import AceFlowResources
    from aceflow_mcp_server.prompts import AceFlowPrompts
    
    # 测试工具
    print("🛠️  MCP 工具测试:")
    tools = AceFlowTools()
    
    # 1. aceflow_init
    print("\n1. 🚀 aceflow_init")
    try:
        result = tools.aceflow_init("minimal", "test-project")
        print(f"   状态: {'✅ 成功' if result.get('success') else '❌ 失败'}")
        if result.get('success'):
            print(f"   项目: {result.get('project_info', {}).get('name', 'N/A')}")
            print(f"   模式: {result.get('project_info', {}).get('mode', 'N/A')}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 2. aceflow_stage
    print("\n2. 📊 aceflow_stage")
    try:
        result = tools.aceflow_stage("list")
        print(f"   状态: {'✅ 成功' if result.get('success') else '❌ 失败'}")
        if result.get('success'):
            stages = result.get('result', {}).get('stages', [])
            print(f"   阶段数量: {len(stages)}")
            print(f"   阶段列表: {', '.join(stages[:3])}{'...' if len(stages) > 3 else ''}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 3. aceflow_validate
    print("\n3. ✅ aceflow_validate")
    try:
        result = tools.aceflow_validate("basic")
        print(f"   状态: {'✅ 成功' if result.get('success') else '❌ 失败'}")
        if result.get('success'):
            validation = result.get('validation_result', {})
            print(f"   验证模式: {validation.get('mode', 'N/A')}")
            print(f"   检查总数: {validation.get('checks_total', 'N/A')}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 4. aceflow_template
    print("\n4. 📋 aceflow_template")
    try:
        result = tools.aceflow_template("list")
        print(f"   状态: {'✅ 成功' if result.get('success') else '❌ 失败'}")
        if result.get('success'):
            templates = result.get('result', {}).get('available_templates', [])
            print(f"   模板数量: {len(templates)}")
            print(f"   可用模板: {', '.join(templates)}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试资源
    print("\n" + "=" * 50)
    print("📚 MCP 资源测试:")
    resources = AceFlowResources()
    
    # 1. project_state
    print("\n1. 📊 project_state")
    try:
        result = resources.project_state("current")
        print(f"   状态: ✅ 成功 (返回 {len(result)} 字符)")
        # 解析 JSON 来显示基本信息
        import json
        state = json.loads(result)
        print(f"   项目状态: {state.get('project', {}).get('status', 'N/A')}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 2. workflow_config
    print("\n2. ⚙️ workflow_config")
    try:
        result = resources.workflow_config("default")
        print(f"   状态: ✅ 成功 (返回 {len(result)} 字符)")
        import json
        config = json.loads(result)
        print(f"   配置状态: {config.get('status', 'N/A')}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 3. stage_guide
    print("\n3. 📖 stage_guide")
    try:
        result = resources.stage_guide("implementation")
        print(f"   状态: ✅ 成功 (返回 {len(result)} 字符)")
        print(f"   指南预览: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试提示
    print("\n" + "=" * 50)
    print("💬 MCP 提示测试:")
    prompts = AceFlowPrompts()
    
    # 1. workflow_assistant
    print("\n1. 🤖 workflow_assistant")
    try:
        result = prompts.workflow_assistant("测试任务", "测试上下文")
        print(f"   状态: ✅ 成功 (返回 {len(result)} 字符)")
        print(f"   提示预览: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 2. stage_guide
    print("\n2. 📋 stage_guide")
    try:
        result = prompts.stage_guide("implementation")
        print(f"   状态: ✅ 成功 (返回 {len(result)} 字符)")
        print(f"   提示预览: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print("\n" + "=" * 50)
    print("📋 总结")
    print("=" * 50)
    print("🎯 AceFlow MCP Server 提供:")
    print("   🛠️  4 个 MCP 工具:")
    print("      - aceflow_init: 项目初始化")
    print("      - aceflow_stage: 阶段管理")
    print("      - aceflow_validate: 项目验证")
    print("      - aceflow_template: 模板管理")
    print()
    print("   📚 3 个 MCP 资源:")
    print("      - aceflow://project/state: 项目状态")
    print("      - aceflow://workflow/config: 工作流配置")
    print("      - aceflow://stage/guide/{stage}: 阶段指导")
    print()
    print("   💬 2 个 MCP 提示:")
    print("      - workflow_assistant: 工作流助手")
    print("      - stage_guide: 阶段指导助手")

if __name__ == "__main__":
    test_aceflow_tools()