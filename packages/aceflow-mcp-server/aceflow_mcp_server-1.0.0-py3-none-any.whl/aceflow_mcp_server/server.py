"""AceFlow MCP Server implementation using FastMCP framework."""

import click
from fastmcp import FastMCP
from .tools import AceFlowTools
from .resources import AceFlowResources
from .prompts import AceFlowPrompts


class AceFlowMCPServer:
    """Main AceFlow MCP Server class."""
    
    def __init__(self):
        """Initialize the MCP server with all tools, resources, and prompts."""
        self.mcp = FastMCP("AceFlow")
        self.tools = AceFlowTools()
        self.resources = AceFlowResources()
        self.prompts = AceFlowPrompts()
        
        self._register_tools()
        self._register_resources()
        self._register_prompts()
    
    def _register_tools(self):
        """Register all AceFlow tools."""
        self.mcp.add_tool(self.tools.aceflow_init)
        self.mcp.add_tool(self.tools.aceflow_stage)
        self.mcp.add_tool(self.tools.aceflow_validate)
        self.mcp.add_tool(self.tools.aceflow_template)
    
    def _register_resources(self):
        """Register all AceFlow resources."""
        self.mcp.add_resource(self.resources.project_state)
        self.mcp.add_resource(self.resources.workflow_config)
        self.mcp.add_resource(self.resources.stage_guide)
    
    def _register_prompts(self):
        """Register all AceFlow prompts."""
        self.mcp.add_prompt(self.prompts.workflow_assistant)
        self.mcp.add_prompt(self.prompts.stage_guide)
    
    def run(self, host: str = "localhost", port: int = 8000, log_level: str = "INFO"):
        """Start the MCP server."""
        self.mcp.run(host=host, port=port, log_level=log_level)


@click.command()
@click.option('--host', default='localhost', help='Host to bind to')
@click.option('--port', default=8000, type=int, help='Port to bind to')
@click.option('--log-level', default='INFO', help='Log level')
@click.version_option(version="1.0.0")
def main(host: str, port: int, log_level: str):
    """Start AceFlow MCP Server."""
    server = AceFlowMCPServer()
    server.run(host=host, port=port, log_level=log_level)


if __name__ == "__main__":
    main()