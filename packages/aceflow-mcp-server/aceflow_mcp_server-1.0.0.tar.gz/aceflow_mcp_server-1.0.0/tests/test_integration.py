"""Integration tests for AceFlow MCP Server."""

import pytest
import tempfile
import os
import json
from pathlib import Path
from aceflow_mcp_server.server import AceFlowMCPServer
from aceflow_mcp_server.tools import AceFlowTools
from aceflow_mcp_server.resources import AceFlowResources
from aceflow_mcp_server.prompts import AceFlowPrompts


class TestIntegration:
    """Integration tests for the complete AceFlow MCP Server."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        self.server = AceFlowMCPServer()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
    
    def test_server_initialization(self):
        """Test that MCP server initializes correctly."""
        assert self.server.mcp is not None
        assert self.server.tools is not None
        assert self.server.resources is not None
        assert self.server.prompts is not None
    
    def test_full_project_workflow(self):
        """Test complete project workflow from initialization to completion."""
        # 1. Initialize project
        init_result = self.server.tools.aceflow_init(
            mode="standard",
            project_name="integration-test"
        )
        assert init_result["success"] is True
        
        # 2. Check project state
        state_result = self.server.resources.project_state()
        state = json.loads(state_result)
        assert state["project"]["name"] == "integration-test"
        assert state["project"]["mode"] == "STANDARD"
        
        # 3. Get workflow config
        config_result = self.server.resources.workflow_config()
        config = json.loads(config_result)
        assert config["status"] == "found"
        
        # 4. Check stage status
        stage_result = self.server.tools.aceflow_stage(action="status")
        assert stage_result["success"] is True
        
        # 5. List available stages
        list_result = self.server.tools.aceflow_stage(action="list")
        assert list_result["success"] is True
        assert len(list_result["result"]["stages"]) > 0
        
        # 6. Validate project
        validate_result = self.server.tools.aceflow_validate()
        assert validate_result["success"] is True
        
        # 7. Check templates
        template_result = self.server.tools.aceflow_template(action="list")
        assert template_result["success"] is True
        assert "standard" in template_result["result"]["available_templates"]
    
    def test_workflow_assistant_prompt_generation(self):
        """Test workflow assistant prompt generation."""
        # Initialize project first
        self.server.tools.aceflow_init(
            mode="complete",
            project_name="prompt-test"
        )
        
        # Generate workflow assistant prompt
        prompt = self.server.prompts.workflow_assistant(
            task="Review project status",
            context="First time setup"
        )
        
        assert "prompt-test" in prompt
        assert "COMPLETE" in prompt
        assert "Review project status" in prompt
        assert "First time setup" in prompt
        assert "aceflow_init" in prompt
        assert "aceflow_stage" in prompt
    
    def test_stage_guide_prompt_generation(self):
        """Test stage guide prompt generation."""
        # Initialize project first
        self.server.tools.aceflow_init(
            mode="minimal",
            project_name="guide-test"
        )
        
        # Generate stage guide prompt
        prompt = self.server.prompts.stage_guide("implementation")
        
        assert "IMPLEMENTATION" in prompt
        assert "guide-test" in prompt
        assert "MINIMAL" in prompt
        assert "implementation" in prompt.lower()
    
    def test_project_mode_consistency(self):
        """Test consistency across different project modes."""
        modes = ["minimal", "standard", "complete", "smart"]
        
        for mode in modes:
            # Create subdirectory for each mode
            mode_dir = Path(f"test-{mode}")
            mode_dir.mkdir()
            
            # Initialize project
            init_result = self.server.tools.aceflow_init(
                mode=mode,
                project_name=f"test-{mode}",
                directory=str(mode_dir)
            )
            assert init_result["success"] is True
            
            # Change to mode directory
            original_dir = os.getcwd()
            os.chdir(mode_dir)
            
            try:
                # Check state consistency
                state_result = self.server.resources.project_state()
                state = json.loads(state_result)
                assert state["project"]["mode"] == mode.upper()
                
                # Check config consistency
                config_result = self.server.resources.workflow_config()
                config = json.loads(config_result)
                assert config["status"] == "found"
                
                # Check prompt generation
                prompt = self.server.prompts.workflow_assistant()
                assert mode.upper() in prompt
                
            finally:
                # Always return to original directory
                os.chdir(original_dir)
    
    def test_resource_and_tool_integration(self):
        """Test integration between resources and tools."""
        # Initialize project
        self.server.tools.aceflow_init(
            mode="standard",
            project_name="resource-tool-test"
        )
        
        # Get initial state
        initial_state = json.loads(self.server.resources.project_state())
        initial_stage = initial_state["flow"]["current_stage"]
        
        # Get stage guide for current stage
        guide = self.server.resources.stage_guide(initial_stage)
        
        # Verify guide contains relevant information
        assert initial_stage.replace("_", " ") in guide.lower() or initial_stage in guide
        assert "## 目标" in guide
        
        # Stage operations should be consistent
        stage_status = self.server.tools.aceflow_stage(action="status")
        assert stage_status["success"] is True
    
    def test_error_handling_integration(self):
        """Test error handling across the integrated system."""
        # Test invalid operations without project
        validate_result = self.server.tools.aceflow_validate()
        # Should succeed but with warnings (mock implementation)
        assert validate_result["success"] is True
        
        # Test resource access without project
        state_result = self.server.resources.project_state()
        state = json.loads(state_result)
        assert state["project"]["status"] == "not_initialized"
        
        # Test invalid stage guide
        invalid_guide = self.server.resources.stage_guide("nonexistent_stage")
        assert "nonexistent_stage" in invalid_guide
        assert "可用阶段指南" in invalid_guide
    
    def test_file_structure_validation(self):
        """Test that the complete file structure is created correctly."""
        result = self.server.tools.aceflow_init(
            mode="complete",
            project_name="structure-test"
        )
        
        assert result["success"] is True
        
        # Verify all expected files and directories exist
        expected_items = [
            ".clinerules",
            ".aceflow/",
            ".aceflow/current_state.json",
            ".aceflow/template.yaml",
            "aceflow_result/",
            "README_ACEFLOW.md"
        ]
        
        for item in expected_items:
            path = Path(item)
            assert path.exists(), f"Expected {item} to exist"
        
        # Verify content of key files
        with open(".aceflow/current_state.json", 'r') as f:
            state = json.load(f)
        assert state["project"]["name"] == "structure-test"
        assert state["project"]["mode"] == "COMPLETE"
        
        with open(".clinerules", 'r') as f:
            clinerules = f.read()
        assert "structure-test" in clinerules
        assert "complete" in clinerules
        
        with open("README_ACEFLOW.md", 'r') as f:
            readme = f.read()
        assert "structure-test" in readme
        assert "COMPLETE" in readme


if __name__ == "__main__":
    pytest.main([__file__])