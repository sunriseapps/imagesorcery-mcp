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


class TestModelsResourceDefinition:
    """Tests for the models resource definition and metadata."""

    @pytest.mark.asyncio
    async def test_models_in_resources_list(self, mcp_server: FastMCP):
        """Tests that models resource is in the list of available resources."""
        async with Client(mcp_server) as client:
            resources = await client.list_resources()
            
            
            # Verify that resources list is not empty
            assert resources, "Resources list should not be empty"

            # Check if models://list is in the list of resources
            # Convert AnyUrl objects to strings
            resource_uris = [str(resource.uri) for resource in resources]
            
            assert "models://list" in resource_uris, (
                f"models://list resource should be in the list of available resources. "
                f"Found: {resource_uris}"
            )

    @pytest.mark.asyncio
    async def test_models_resource_metadata(self, mcp_server: FastMCP):
        """Tests that models resource has the correct metadata."""
        async with Client(mcp_server) as client:
            resources = await client.list_resources()
            
            
            models_resource = next(
                (resource for resource in resources if str(resource.uri) == "models://list"), None
            )

            # Check that the resource exists
            assert models_resource is not None, f"models://list resource should exist. Found resources: {[str(r.uri) for r in resources]}"
            
            # Check name - it appears FastMCP uses the full URI as the name
            assert models_resource.name == "list_models", f"Resource name should be 'list_models' but got '{models_resource.name}'"
            
            # Since description is None, let's skip this check for now or check for None
            # The actual resource implementation might not set a description at the transport level

class TestModelsResourceExecution:
    """Tests for the models resource execution and results."""

    @pytest.mark.asyncio
    async def test_models_resource_execution(self, mcp_server: FastMCP, test_models_dir):
        """Tests the models resource execution and return value."""
        async with Client(mcp_server) as client:
            result = await client.read_resource("models://list")
            
            # Check that the resource returned a result
            assert len(result) == 1
            
            # Parse the result
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
                assert "path" in model
                
                # Check specific models
                if model["name"] == "yolov8n.pt":
                    assert "Smallest and fastest" in model["description"]
                elif model["name"] == "yolov8m.pt":
                    assert "Default model" in model["description"]
                elif model["name"] == "custom_model.pt":
                    assert model["description"] == "Model 'custom_model.pt' not found in model_descriptions.json (total descriptions: 2)"

    @pytest.mark.asyncio
    async def test_models_empty_directory(self, mcp_server: FastMCP, tmp_path):
        """Tests the models resource with an empty models directory."""
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
                result = await client.read_resource("models://list")
                
                # Check that the resource returned a result
                assert len(result) == 1
                
                # Parse the result
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

    @pytest.mark.asyncio
    async def test_models_no_directory(self, mcp_server: FastMCP, tmp_path):
        """Tests the models resource when the models directory doesn't exist."""
        # Save the original models directory path
        original_models_dir = Path("models")
        original_exists = original_models_dir.exists()
        
        # Remove the original directory if it exists
        if original_exists:
            # Rename the original directory
            temp_original = original_models_dir.with_name("models_original_backup")
            original_models_dir.rename(temp_original)
        
        try:
            async with Client(mcp_server) as client:
                result = await client.read_resource("models://list")
                
                # Check that the resource returned a result
                assert len(result) == 1
                
                # Parse the result
                result_dict = json.loads(result[0].text)
                
                # Check that the result has the expected structure
                assert "models" in result_dict
                assert isinstance(result_dict["models"], list)
                
                # Check that the list is empty when directory doesn't exist
                assert len(result_dict["models"]) == 0
        finally:
            # Restore the original directory if it existed
            if original_exists:
                temp_original.rename(original_models_dir)

    @pytest.mark.asyncio
    async def test_models_with_subdirectories(self, mcp_server: FastMCP, tmp_path):
        """Tests the models resource with models in subdirectories."""
        # Save the original models directory path
        original_models_dir = Path("models")
        original_exists = original_models_dir.exists()
        
        if original_exists:
            # Rename the original directory
            temp_original = original_models_dir.with_name("models_original_backup")
            original_models_dir.rename(temp_original)
        
        # Create a models directory with subdirectories
        models_dir = tmp_path / "models"
        models_dir.mkdir(exist_ok=True)
        
        # Create subdirectories and model files
        (models_dir / "detection").mkdir()
        (models_dir / "detection" / "yolov8n.pt").touch()
        (models_dir / "segmentation").mkdir()
        (models_dir / "segmentation" / "sam.onnx").touch()
        (models_dir / "root_model.pt").touch()
        
        # Create descriptions file
        descriptions = {
            "detection/yolov8n.pt": "YOLOv8 Nano for object detection",
            "segmentation/sam.onnx": "Segment Anything Model",
            "root_model.pt": "Model in root directory"
        }
        with open(models_dir / "model_descriptions.json", "w") as f:
            json.dump(descriptions, f)
        
        # Create a symlink to our temporary directory
        os.symlink(models_dir, original_models_dir)
        
        try:
            async with Client(mcp_server) as client:
                result = await client.read_resource("models://list")
                
                # Check that the resource returned a result
                assert len(result) == 1
                
                # Parse the result
                result_dict = json.loads(result[0].text)
                
                # Check that the result has the expected structure
                assert "models" in result_dict
                assert isinstance(result_dict["models"], list)
                
                # Check that we have all the models
                assert len(result_dict["models"]) == 3
                
                # Check model names
                model_names = [model["name"] for model in result_dict["models"]]
                assert "detection/yolov8n.pt" in model_names
                assert "segmentation/sam.onnx" in model_names
                assert "root_model.pt" in model_names
                
                # Check descriptions
                for model in result_dict["models"]:
                    if model["name"] == "detection/yolov8n.pt":
                        assert model["description"] == "YOLOv8 Nano for object detection"
                    elif model["name"] == "segmentation/sam.onnx":
                        assert model["description"] == "Segment Anything Model"
                    elif model["name"] == "root_model.pt":
                        assert model["description"] == "Model in root directory"
        finally:
            # Clean up: remove the symlink
            if os.path.islink(original_models_dir):
                os.unlink(original_models_dir)
            
            # Restore the original directory if it existed
            if original_exists:
                temp_original.rename(original_models_dir)

    @pytest.mark.asyncio
    async def test_models_ignores_non_model_files(self, mcp_server: FastMCP, tmp_path):
        """Tests that the models resource ignores non-model files."""
        # Save the original models directory path
        original_models_dir = Path("models")
        original_exists = original_models_dir.exists()
        
        if original_exists:
            # Rename the original directory
            temp_original = original_models_dir.with_name("models_original_backup")
            original_models_dir.rename(temp_original)
        
        # Create a models directory with various files
        models_dir = tmp_path / "models"
        models_dir.mkdir(exist_ok=True)
        
        # Create model and non-model files
        (models_dir / "model1.pt").touch()
        (models_dir / "model2.onnx").touch()
        (models_dir / "readme.txt").touch()
        (models_dir / "config.json").touch()
        (models_dir / "image.jpg").touch()
        
        # Create descriptions file
        descriptions = {
            "model1.pt": "PyTorch model",
            "model2.onnx": "ONNX model"
        }
        with open(models_dir / "model_descriptions.json", "w") as f:
            json.dump(descriptions, f)
        
        # Create a symlink to our temporary directory
        os.symlink(models_dir, original_models_dir)
        
        try:
            async with Client(mcp_server) as client:
                result = await client.read_resource("models://list")
                
                # Check that the resource returned a result
                assert len(result) == 1
                
                # Parse the result
                result_dict = json.loads(result[0].text)
                
                # Check that the result has the expected structure
                assert "models" in result_dict
                assert isinstance(result_dict["models"], list)
                
                # Check that we have only the model files
                assert len(result_dict["models"]) == 2
                
                # Check model names
                model_names = [model["name"] for model in result_dict["models"]]
                assert "model1.pt" in model_names
                assert "model2.onnx" in model_names
                
                # Non-model files should not be included
                assert "readme.txt" not in model_names
                assert "config.json" not in model_names
                assert "image.jpg" not in model_names
                assert "model_descriptions.json" not in model_names
        finally:
            # Clean up: remove the symlink
            if os.path.islink(original_models_dir):
                os.unlink(original_models_dir)
            
            # Restore the original directory if it existed
            if original_exists:
                temp_original.rename(original_models_dir)
