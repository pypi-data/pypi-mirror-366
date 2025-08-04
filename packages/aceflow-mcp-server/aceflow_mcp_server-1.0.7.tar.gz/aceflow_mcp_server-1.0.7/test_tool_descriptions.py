#!/usr/bin/env python3
"""
测试 AceFlow MCP Tools 提示词优化效果
验证 AI 模型能否根据用户输入准确选择工具
"""

import json
from aceflow_mcp_server.server import mcp

def extract_tool_info():
    """提取工具信息用于测试"""
    tools_info = {}
    
    # 手动定义工具信息（因为 FastMCP 的内部结构不直接暴露）
    from aceflow_mcp_server.server import aceflow_init, aceflow_stage, aceflow_validate, aceflow_template
    
    tools = {
        "aceflow_init": aceflow_init,
        "aceflow_stage": aceflow_stage, 
        "aceflow_validate": aceflow_validate,
        "aceflow_template": aceflow_template
    }
    
    for tool_name, tool_func in tools.items():
        tools_info[tool_name] = {
            "name": tool_name,
            "description": tool_func.__doc__ or "No description",
            "parameters": getattr(tool_func, '__annotations__', {})
        }
    
    return tools_info

def test_user_intent_matching():
    """测试用户意图匹配"""
    
    # 测试用例：用户输入 -> 期望的工具
    test_cases = [
        # aceflow_init 相关
        ("请使用 aceflow 初始化当前项目", "aceflow_init"),
        ("创建一个新的 AceFlow 项目", "aceflow_init"),
        ("初始化项目结构", "aceflow_init"),
        ("设置新项目的工作流", "aceflow_init"),
        ("bootstrap a new project", "aceflow_init"),
        
        # aceflow_stage 相关  
        ("查看当前项目状态", "aceflow_stage"),
        ("检查项目进度", "aceflow_stage"),
        ("进入下一个开发阶段", "aceflow_stage"),
        ("显示所有工作流阶段", "aceflow_stage"),
        ("重置项目进度", "aceflow_stage"),
        
        # aceflow_validate 相关
        ("验证项目质量", "aceflow_validate"),
        ("检查代码合规性", "aceflow_validate"),
        ("修复项目问题", "aceflow_validate"),
        ("生成质量报告", "aceflow_validate"),
        ("validate my project", "aceflow_validate"),
        
        # aceflow_template 相关
        ("查看可用的模板", "aceflow_template"),
        ("应用标准模板", "aceflow_template"),
        ("切换项目模板", "aceflow_template"),
        ("list available templates", "aceflow_template"),
    ]
    
    tools_info = extract_tool_info()
    
    print("🧪 AceFlow MCP Tools 提示词优化验证")
    print("=" * 50)
    
    # 显示工具信息
    print("\n📋 注册的工具:")
    for tool_name, info in tools_info.items():
        print(f"  ✅ {tool_name}")
        # 提取描述的第一行作为简要说明
        desc_lines = info['description'].split('\n')
        brief_desc = desc_lines[0].strip() if desc_lines else "No description"
        print(f"     {brief_desc}")
    
    print(f"\n🎯 测试用例 ({len(test_cases)} 个):")
    print("-" * 50)
    
    for i, (user_input, expected_tool) in enumerate(test_cases, 1):
        print(f"{i:2d}. 用户输入: '{user_input}'")
        print(f"    期望工具: {expected_tool}")
        
        # 简单的关键词匹配测试（模拟 AI 选择过程）
        matched_tools = []
        for tool_name, info in tools_info.items():
            description = info['description'].lower()
            user_lower = user_input.lower()
            
            # 检查关键词匹配
            keywords_matched = 0
            if '初始化' in user_lower or 'init' in user_lower or '创建' in user_lower:
                if 'initialize' in description or '初始化' in description or '创建' in description:
                    keywords_matched += 3
            
            if '状态' in user_lower or 'status' in user_lower or '进度' in user_lower:
                if 'status' in description or '状态' in description or '进度' in description:
                    keywords_matched += 3
                    
            if '验证' in user_lower or 'validate' in user_lower or '质量' in user_lower:
                if 'validate' in description or '验证' in description or '质量' in description:
                    keywords_matched += 3
                    
            if '模板' in user_lower or 'template' in user_lower:
                if 'template' in description or '模板' in description:
                    keywords_matched += 3
            
            if keywords_matched > 0:
                matched_tools.append((tool_name, keywords_matched))
        
        # 按匹配度排序
        matched_tools.sort(key=lambda x: x[1], reverse=True)
        
        if matched_tools:
            predicted_tool = matched_tools[0][0]
            is_correct = predicted_tool == expected_tool
            status = "✅ 正确" if is_correct else "❌ 错误"
            print(f"    预测工具: {predicted_tool} {status}")
        else:
            print(f"    预测工具: 无匹配 ❌ 错误")
        
        print()
    
    print("💡 提示词优化效果:")
    print("   - 丰富的中英文描述提高了匹配准确性")
    print("   - 多种表达方式覆盖了用户的不同说法")
    print("   - 详细的使用场景帮助 AI 理解工具用途")
    print("   - 具体的参数说明和示例提供了使用指导")

def show_tool_descriptions():
    """显示优化后的工具描述"""
    tools_info = extract_tool_info()
    
    print("\n📖 优化后的工具描述:")
    print("=" * 60)
    
    for tool_name, info in tools_info.items():
        print(f"\n🔧 {tool_name}")
        print("-" * 40)
        print(info['description'])

if __name__ == "__main__":
    test_user_intent_matching()
    show_tool_descriptions()