#!/usr/bin/env python3
"""
AceFlow MCP Server 集成测试
验证所有工具功能和连接稳定性
"""

import asyncio
import json
import logging
import sys
import time
from typing import Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MCPIntegrationTest:
    """MCP 集成测试类"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
    
    def log_test_result(self, test_name: str, success: bool, message: str = "", duration: float = 0):
        """记录测试结果"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {message} ({duration:.2f}s)")
    
    async def test_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """测试单个工具调用"""
        test_start = time.time()
        
        try:
            # 这里我们模拟工具调用，实际测试中会通过MCP协议调用
            from aceflow_mcp_server.tools import AceFlowTools
            tools = AceFlowTools()
            
            if tool_name == "aceflow_init":
                result = tools.aceflow_init(**arguments)
            elif tool_name == "aceflow_stage":
                result = tools.aceflow_stage(**arguments)
            elif tool_name == "aceflow_validate":
                result = tools.aceflow_validate(**arguments)
            elif tool_name == "aceflow_template":
                result = tools.aceflow_template(**arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            duration = time.time() - test_start
            
            # 验证结果格式
            if isinstance(result, dict) and "success" in result:
                self.log_test_result(
                    f"Tool {tool_name}",
                    result.get("success", False),
                    f"Result: {result.get('message', 'OK')}",
                    duration
                )
                return result.get("success", False)
            else:
                self.log_test_result(
                    f"Tool {tool_name}",
                    False,
                    "Invalid result format",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - test_start
            self.log_test_result(
                f"Tool {tool_name}",
                False,
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    async def test_output_adapter(self) -> bool:
        """测试输出适配器"""
        test_start = time.time()
        
        try:
            from aceflow_mcp_server.mcp_output_adapter import MCPOutputAdapter
            adapter = MCPOutputAdapter()
            
            # 测试各种输入类型
            test_cases = [
                {"input": "Hello World", "expected_type": "text"},
                {"input": {"key": "value"}, "expected_type": "text"},
                {"input": ["item1", "item2"], "expected_type": "text"},
                {"input": None, "expected_type": "text"},
                {"input": 123, "expected_type": "text"},
            ]
            
            all_passed = True
            for case in test_cases:
                result = adapter.convert_to_mcp_format(case["input"])
                
                # 验证MCP格式
                if not adapter.validate_mcp_format(result):
                    all_passed = False
                    break
                
                # 验证内容类型
                if result["content"][0]["type"] != case["expected_type"]:
                    all_passed = False
                    break
            
            duration = time.time() - test_start
            self.log_test_result(
                "Output Adapter",
                all_passed,
                f"Tested {len(test_cases)} cases",
                duration
            )
            return all_passed
            
        except Exception as e:
            duration = time.time() - test_start
            self.log_test_result(
                "Output Adapter",
                False,
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    async def test_performance(self) -> bool:
        """测试性能"""
        test_start = time.time()
        
        try:
            # 连续调用工具测试性能
            call_count = 10
            successful_calls = 0
            total_duration = 0
            
            for i in range(call_count):
                call_start = time.time()
                success = await self.test_tool_call("aceflow_stage", {"action": "list"})
                call_duration = time.time() - call_start
                total_duration += call_duration
                
                if success:
                    successful_calls += 1
            
            avg_duration = total_duration / call_count
            success_rate = successful_calls / call_count
            
            # 性能标准：平均响应时间 < 1秒，成功率 > 90%
            performance_ok = avg_duration < 1.0 and success_rate > 0.9
            
            duration = time.time() - test_start
            self.log_test_result(
                "Performance Test",
                performance_ok,
                f"Avg: {avg_duration:.2f}s, Success: {success_rate:.1%}",
                duration
            )
            return performance_ok
            
        except Exception as e:
            duration = time.time() - test_start
            self.log_test_result(
                "Performance Test",
                False,
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        logger.info("🚀 开始 AceFlow MCP Server 集成测试")
        
        # 测试输出适配器
        await self.test_output_adapter()
        
        # 测试所有工具
        test_cases = [
            ("aceflow_stage", {"action": "list"}),
            ("aceflow_stage", {"action": "status"}),
            ("aceflow_template", {"action": "list"}),
            ("aceflow_validate", {"mode": "basic"}),
            # 注意：aceflow_init 可能会修改文件系统，在测试中谨慎使用
        ]
        
        for tool_name, arguments in test_cases:
            await self.test_tool_call(tool_name, arguments)
        
        # 性能测试
        await self.test_performance()
        
        # 计算总体结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_duration = time.time() - self.start_time
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "total_duration": total_duration,
            "results": self.test_results
        }
        
        # 输出测试摘要
        logger.info("📊 测试摘要:")
        logger.info(f"   总测试数: {total_tests}")
        logger.info(f"   通过测试: {passed_tests}")
        logger.info(f"   失败测试: {total_tests - passed_tests}")
        logger.info(f"   成功率: {summary['success_rate']:.1%}")
        logger.info(f"   总耗时: {total_duration:.2f}秒")
        
        if summary['success_rate'] >= 0.8:
            logger.info("🎉 集成测试通过！")
        else:
            logger.error("💥 集成测试失败！")
        
        return summary


async def main():
    """主函数"""
    test_runner = MCPIntegrationTest()
    
    try:
        summary = await test_runner.run_all_tests()
        
        # 输出详细结果到文件
        with open("mcp_test_results.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # 根据测试结果设置退出码
        if summary['success_rate'] >= 0.8:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"测试运行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())