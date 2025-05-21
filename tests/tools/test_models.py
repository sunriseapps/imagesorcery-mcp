import json
import os
from pathlib import Path

import pytest
from fastmcp import Client, FastMCP

from imagesorcery_mcp.server import mcp as image_sorcery_mcp_server


@pytest.fixture
def mcp_server():
    # Use the existing server instance
    return image_sorcery_mcp_server


@pytest.fixture
def test_models_dir(tmp_path):
    """Create a temporary models directory with test model files."""
    # Save the original models directory path
    original_models_dir = Path("models")
    original_exists = original_models_dir.exists()
    
    # Create a temporary models directory
    models_dir = tmp_path / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Create some test model files
    test_models = ["yolov8n.pt", "yolov8m.pt", "custom_model.pt"]
    for model_name in test_models:
        model_path = models_dir / model_name
        # Create an empty file
        model_path.touch()
    
    # Create a test model descriptions file
    descriptions = {
        "yolov8n.pt": "YOLOv8 Nano - Smallest and fastest model, suitable for edge devices with limited resources.",
        "yolov8m.pt": "YOLOv8 Medium - Default model with good balance between accuracy and speed."
    }
    with open(models_dir / "model_descriptions.json", "w") as f:
        json.dump(descriptions, f)
    
    # Temporarily replace the models directory
    if original_exists:
        # Rename the original directory
        temp_original = original_models_dir.with_name("models_original_backup")
        original_models_dir.rename(temp_original)
    
    # Create a symlink to our temporary directory
    os.symlink(models_dir, original_models_dir)
    
    yield models_dir
    
    # Clean up: remove the symlink
    if os.path.islink(original_models_dir):
        os.unlink(original_models_dir)
    
    # Restore the original directory if it existed
    if original_exists:
        temp_original.rename(original_models_dir)


class TestModelsToolDefinition:
    """Tests for the models tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_models_in_tools_list(self, mcp_server: FastMCP):
        """Tests that models tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"

            # Check if get_models is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "get_models" in tool_names, (
                "get_models tool should be in the list of available tools"
            )

    @pytest.mark.asyncio
    async def test_models_description(self, mcp_server: FastMCP):
        """Tests that models tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            models_tool = next(
                (tool for tool in tools if tool.name == "get_models"), None
            )

            # Check description
            assert models_tool.description, "get_models tool should have a description"
            assert "list" in models_tool.description.lower(), (
                "Description should mention that it lists available models"
            )

    @pytest.mark.asyncio
    async def test_models_parameters(self, mcp_server: FastMCP):
        """Tests that models tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            models_tool = next(
                (tool for tool in tools if tool.name == "get_models"), None
            )

            # Check that the tool doesn't require any input parameters
            assert not models_tool.inputSchema.get("required", []), (
                "get_models tool should not have any required parameters"
            )


class TestModelsToolExecution:
    """Tests for the models tool execution and results."""

    @pytest.mark.asyncio
    async def test_models_tool_execution(self, mcp_server: FastMCP, test_models_dir):
        """Tests the models tool execution and return value."""
        async with Client(mcp_server) as client:
            result = await client.call_tool("get_models", {})

            # Check that the tool returned a result
            assert len(result) == 1
            
            # Parse the result
            import json
            result_dict = json.loads(result[0].text)
            
            # Check that the result has the expected structure
            assert "models" in result_dict
            assert isinstance(result_dict["models"], list)
            
            # Check that we have the expected number of models
            assert len(result_dict["models"]) == 3
            
            # Check that each model has the expected fields
            for model in result_dict["models"]:
                assert "name" in model
                assert "description" in model
                
                # Check specific models
                if model["name"] == "yolov8n.pt":
                    assert "Smallest and fastest" in model["description"]
                elif model["name"] == "yolov8m.pt":
                    assert "Default model" in model["description"]
                elif model["name"] == "custom_model.pt":
                    assert model["description"] == "Model 'custom_model.pt' not found in model_descriptions.json (total descriptions: 2)"

    @pytest.mark.asyncio
    async def test_models_empty_directory(self, mcp_server: FastMCP, tmp_path):
        """Tests the models tool with an empty models directory."""
        # Save the original models directory path
        original_models_dir = Path("models")
        original_exists = original_models_dir.exists()
        
        if original_exists:
            # Rename the original directory
            temp_original = original_models_dir.with_name("models_original_backup")
            original_models_dir.rename(temp_original)
        
        # Create an empty models directory
        empty_models_dir = tmp_path / "empty_models"
        empty_models_dir.mkdir(exist_ok=True)
        os.symlink(empty_models_dir, original_models_dir)
        
        try:
            async with Client(mcp_server) as client:
                result = await client.call_tool("get_models", {})
                
                # Check that the tool returned a result
                assert len(result) == 1
                
                # Parse the result
                import json
                result_dict = json.loads(result[0].text)
                
                # Check that the result has the expected structure
                assert "models" in result_dict
                assert isinstance(result_dict["models"], list)
                
                # Check that the list is empty
                assert len(result_dict["models"]) == 0
        finally:
            # Clean up: remove the symlink
            if os.path.islink(original_models_dir):
                os.unlink(original_models_dir)
            
            # Restore the original directory if it existed
            if original_exists:
                temp_original.rename(original_models_dir)
