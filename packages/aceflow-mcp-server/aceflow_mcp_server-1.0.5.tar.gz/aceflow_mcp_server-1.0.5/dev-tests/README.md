# Development Tests

This directory contains development tests, experiments, and debugging tools for AceFlow MCP Server.

## Purpose

These tests are used for:
- Development and debugging
- Experimental features
- Integration testing
- Protocol validation
- Performance testing

## Files

### Core Testing
- `test_mcp_integration.py` - Comprehensive integration tests
- `test_enhanced_prompts.py` - Test enhanced prompt functionality
- `test_mcp_protocol.py` - MCP protocol compliance tests

### Connection Testing
- `test_stdio_mcp.py` - Test stdio transport mode
- `test_tool_registration.py` - Test tool registration process
- `test_mcp_server.py` - Test MCP server functionality

### Specific Feature Tests
- `test_mcp_tools.py` - Test individual MCP tools
- `test_package_content.py` - Test package content and structure
- `test_mcp_async.py` - Test asynchronous MCP operations
- `test_fastmcp.py` - Test FastMCP framework integration

## Usage

### Running Individual Tests
```bash
python dev-tests/test_mcp_integration.py
python dev-tests/test_enhanced_prompts.py
```

### Running All Development Tests
```bash
# Run all tests in the directory
python -m pytest dev-tests/
```

## Note

These tests are for development purposes and may:
- Modify the file system
- Create temporary files
- Require specific environment setup
- Take longer to run than unit tests

For production testing, use the tests in the `tests/` directory instead.

## Output

Test outputs and logs are typically written to:
- `dev-tests/output/` (ignored by git)
- Individual `*.log` files (ignored by git)
- Console output for immediate feedback