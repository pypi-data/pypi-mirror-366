"""AceFlow MCP Server implementation using FastMCP framework."""

import click
from fastmcp import FastMCP
from typing import Dict, Any, Optional

# Create global FastMCP instance
mcp = FastMCP("AceFlow")

# Initialize components (import after mcp creation to avoid circular imports)
def get_tools():
    from .tools import AceFlowTools
    return AceFlowTools()

def get_resources():
    from .resources import AceFlowResources
    return AceFlowResources()

def get_prompts():
    from .prompts import AceFlowPrompts
    return AceFlowPrompts()

# Register tools with decorators
@mcp.tool
def aceflow_init(
    mode: str,
    project_name: Optional[str] = None,
    directory: Optional[str] = None
) -> Dict[str, Any]:
    """Initialize AceFlow project with specified mode."""
    tools = get_tools()
    return tools.aceflow_init(mode, project_name, directory)

@mcp.tool
def aceflow_stage(
    action: str,
    stage: Optional[str] = None
) -> Dict[str, Any]:
    """Manage project stages and workflow."""
    tools = get_tools()
    return tools.aceflow_stage(action, stage)

@mcp.tool
def aceflow_validate(
    mode: str = "basic",
    fix: bool = False,
    report: bool = False
) -> Dict[str, Any]:
    """Validate project compliance and quality."""
    tools = get_tools()
    return tools.aceflow_validate(mode, fix, report)

@mcp.tool
def aceflow_template(
    action: str,
    template: Optional[str] = None
) -> Dict[str, Any]:
    """Manage workflow templates."""
    tools = get_tools()
    return tools.aceflow_template(action, template)

# Register resources with decorators
@mcp.resource("aceflow://project/state/{project_id}")
def project_state(project_id: str = "current") -> str:
    """Get current project state."""
    resources = get_resources()
    return resources.project_state(project_id)

@mcp.resource("aceflow://workflow/config/{config_id}")
def workflow_config(config_id: str = "default") -> str:
    """Get workflow configuration."""
    resources = get_resources()
    return resources.workflow_config(config_id)

@mcp.resource("aceflow://stage/guide/{stage}")
def stage_guide(stage: str) -> str:
    """Get stage-specific guidance."""
    resources = get_resources()
    return resources.stage_guide(stage)

# Register prompts with decorators
@mcp.prompt
def workflow_assistant(
    task: Optional[str] = None,
    context: Optional[str] = None
) -> str:
    """Generate workflow assistance prompt."""
    prompts = get_prompts()
    return prompts.workflow_assistant(task, context)

@mcp.prompt
def stage_guide_prompt(stage: str) -> str:
    """Generate stage-specific guidance prompt."""
    prompts = get_prompts()
    return prompts.stage_guide(stage)


class AceFlowMCPServer:
    """Main AceFlow MCP Server class."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.mcp = mcp
    
    def run(self, host: str = "localhost", port: int = 8000, log_level: str = "INFO"):
        """Start the MCP server."""
        self.mcp.run(host=host, port=port, log_level=log_level)


@click.command()
@click.option('--host', default='localhost', help='Host to bind to')
@click.option('--port', default=8000, type=int, help='Port to bind to')
@click.option('--log-level', default='INFO', help='Log level')
@click.version_option(version="1.0.2")
def main(host: str, port: int, log_level: str):
    """Start AceFlow MCP Server."""
    server = AceFlowMCPServer()
    server.run(host=host, port=port, log_level=log_level)


if __name__ == "__main__":
    main()