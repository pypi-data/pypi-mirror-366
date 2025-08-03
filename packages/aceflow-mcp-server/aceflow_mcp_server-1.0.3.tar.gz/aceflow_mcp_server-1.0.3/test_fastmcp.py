#!/usr/bin/env python3
"""Test FastMCP usage."""

from fastmcp import FastMCP
from fastmcp.tools import tool
from fastmcp.resources import resource
from fastmcp.prompts import prompt

# Test tool decorator
@tool
def test_tool(name: str) -> str:
    """Test tool function."""
    return f"Hello {name}!"

# Test resource decorator
@resource("test://resource")
def test_resource() -> str:
    """Test resource function."""
    return "Test resource content"

# Test prompt decorator
@prompt
def test_prompt(message: str) -> str:
    """Test prompt function."""
    return f"Test prompt: {message}"

if __name__ == "__main__":
    print("Testing FastMCP decorators...")
    print(f"Tool result: {test_tool('World')}")
    print(f"Resource result: {test_resource()}")
    print(f"Prompt result: {test_prompt('Hello')}")
    print("All tests passed!") 