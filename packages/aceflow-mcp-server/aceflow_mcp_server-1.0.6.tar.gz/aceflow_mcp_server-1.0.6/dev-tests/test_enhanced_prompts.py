#!/usr/bin/env python3
"""
测试增强的工具提示词功能
"""

from aceflow_mcp_server.tool_prompts import AceFlowToolPrompts
from aceflow_mcp_server.prompt_generator import AceFlowPromptGenerator

def test_tool_definitions():
    """测试工具定义"""
    print("🔧 测试工具定义...")
    
    tool_prompts = AceFlowToolPrompts()
    definitions = tool_prompts.get_tool_definitions()
    
    print(f"✅ 找到 {len(definitions)} 个工具定义")
    
    for tool_name, tool_def in definitions.items():
        print(f"\n📋 {tool_name}:")
        print(f"   描述: {tool_def['description']}")
        print(f"   示例数量: {len(tool_def.get('usage_examples', []))}")

def test_prompt_generator():
    """测试提示词生成器"""
    print("\n🎯 测试提示词生成器...")
    
    generator = AceFlowPromptGenerator()
    
    # 测试上下文提示词
    contexts = ["general", "project_start", "development", "debugging"]
    
    for context in contexts:
        prompt = generator.generate_context_prompt(context)
        print(f"\n📝 {context} 上下文提示词长度: {len(prompt)} 字符")
    
    # 测试工具特定提示词
    tool_names = ["aceflow_init", "aceflow_stage", "aceflow_validate", "aceflow_template"]
    
    for tool_name in tool_names:
        prompt = generator.generate_tool_specific_prompt(tool_name)
        print(f"🔧 {tool_name} 工具提示词长度: {len(prompt)} 字符")

def test_workflow_prompt():
    """测试工作流提示词"""
    print("\n📊 测试工作流提示词...")
    
    generator = AceFlowPromptGenerator()
    
    # 测试不同阶段的工作流提示词
    stages = ["user_stories", "implementation", "demo", None]
    
    for stage in stages:
        prompt = generator.generate_workflow_prompt(stage)
        stage_name = stage or "未知阶段"
        print(f"🔄 {stage_name} 工作流提示词长度: {len(prompt)} 字符")

def show_sample_prompts():
    """显示示例提示词"""
    print("\n🎨 示例提示词展示...")
    
    generator = AceFlowPromptGenerator()
    
    # 显示项目启动提示词
    print("\n" + "="*60)
    print("📋 项目启动提示词示例:")
    print("="*60)
    prompt = generator.generate_context_prompt("project_start")
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    
    # 显示工具特定提示词
    print("\n" + "="*60)
    print("🔧 aceflow_init 工具提示词示例:")
    print("="*60)
    prompt = generator.generate_tool_specific_prompt("aceflow_init")
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)

if __name__ == "__main__":
    print("🚀 AceFlow 增强提示词测试")
    print("="*50)
    
    test_tool_definitions()
    test_prompt_generator()
    test_workflow_prompt()
    show_sample_prompts()
    
    print("\n🎉 所有测试完成！")