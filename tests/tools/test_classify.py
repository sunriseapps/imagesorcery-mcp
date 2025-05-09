import json
import os

import pytest
from fastmcp import Client, FastMCP

from imagewizard_mcp.server import mcp as image_wizard_mcp_server


@pytest.fixture
def mcp_server():
    # Use the existing server instance
    return image_wizard_mcp_server


@pytest.fixture
def test_images_paths():
    """Paths to test images for classification."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = os.path.join(os.path.dirname(current_dir), "data")
    
    # Group 1: Outdoor images
    outdoor_images = [
        os.path.join(test_data_dir, f"test_classify_{i}.jpg") for i in range(1, 3)
    ]
    
    # Group 2: Indoor images
    indoor_images = [
        os.path.join(test_data_dir, f"test_classify_{i}.jpg") for i in range(3, 5)
    ]
    
    return {
        "outdoor": outdoor_images,
        "indoor": indoor_images,
        "all": outdoor_images + indoor_images
    }


class TestClassifyToolDefinition:
    """Tests for the classify tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_classify_in_tools_list(self, mcp_server: FastMCP):
        """Tests that classify tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"

            # Check if classify is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "classify" in tool_names, (
                "classify tool should be in the list of available tools"
            )

    @pytest.mark.asyncio
    async def test_classify_description(self, mcp_server: FastMCP):
        """Tests that classify tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            classify_tool = next((tool for tool in tools if tool.name == "classify"), None)

            # Check description
            assert classify_tool.description, "classify tool should have a description"
            assert "classify" in classify_tool.description.lower(), (
                "Description should mention that it classifies images"
            )

    @pytest.mark.asyncio
    async def test_classify_parameters(self, mcp_server: FastMCP):
        """Tests that classify tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            classify_tool = next((tool for tool in tools if tool.name == "classify"), None)

            # Check input schema
            assert hasattr(classify_tool, "inputSchema"), (
                "classify tool should have an inputSchema"
            )
            assert "properties" in classify_tool.inputSchema, (
                "inputSchema should have properties field"
            )

            # Check required parameters
            required_params = ["input_path", "categories"]
            for param in required_params:
                assert param in classify_tool.inputSchema["properties"], (
                    f"classify tool should have a '{param}' property in its inputSchema"
                )


class TestClassifyToolExecution:
    """Tests for the classify tool execution and results."""

    @pytest.mark.asyncio
    async def test_classify_with_categories(self, mcp_server: FastMCP, test_images_paths):
        """Tests the classify tool execution with categories."""
        # Get an outdoor image for testing
        test_image_path = test_images_paths["outdoor"][0]
        
        # Skip if test image doesn't exist
        if not os.path.exists(test_image_path):
            pytest.skip(f"Test image not found at {test_image_path}")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "classify",
                {
                    "input_path": test_image_path,
                    "categories": ["indoor", "outdoor"]
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1

            # Parse the result
            classification_result = json.loads(result[0].text)

            # Basic structure checks
            assert "image_path" in classification_result
            assert "classifications" in classification_result
            assert classification_result["image_path"] == test_image_path
            assert isinstance(classification_result["classifications"], list)

            # Check that we have classifications for both categories
            assert len(classification_result["classifications"]) == 2
            
            # Check the structure of a classification
            classification = classification_result["classifications"][0]
            assert "category" in classification, "Classification should have a category name"
            assert "confidence" in classification, "Classification should have a confidence score"

            # Check that the confidence is within expected range
            assert 0 <= classification["confidence"] <= 1, (
                "Confidence should be between 0 and 1"
            )

    @pytest.mark.asyncio
    async def test_classify_outdoor_images(self, mcp_server: FastMCP, test_images_paths):
        """Tests that outdoor images are correctly classified."""
        # Skip if any test image doesn't exist
        for img_path in test_images_paths["outdoor"]:
            if not os.path.exists(img_path):
                pytest.skip(f"Test image not found at {img_path}")
        
        async with Client(mcp_server) as client:
            for test_image_path in test_images_paths["outdoor"]:
                result = await client.call_tool(
                    "classify",
                    {
                        "input_path": test_image_path,
                        "categories": ["indoor", "outdoor"]
                    },
                )
                
                # Parse the result
                classification_result = json.loads(result[0].text)
                
                # Get confidence scores by category
                categories = {c["category"]: c["confidence"] for c in classification_result["classifications"]}
                
                # Check that both categories have confidence scores
                assert "indoor" in categories
                assert "outdoor" in categories
                
                # Check that confidence scores are within range
                assert 0 <= categories["indoor"] <= 1
                assert 0 <= categories["outdoor"] <= 1

    @pytest.mark.asyncio
    async def test_classify_indoor_images(self, mcp_server: FastMCP, test_images_paths):
        """Tests that indoor images are correctly classified."""
        # Skip if any test image doesn't exist
        for img_path in test_images_paths["indoor"]:
            if not os.path.exists(img_path):
                pytest.skip(f"Test image not found at {img_path}")
        
        async with Client(mcp_server) as client:
            for test_image_path in test_images_paths["indoor"]:
                result = await client.call_tool(
                    "classify",
                    {
                        "input_path": test_image_path,
                        "categories": ["indoor", "outdoor"]
                    },
                )
                
                # Parse the result
                classification_result = json.loads(result[0].text)
                
                # Get confidence scores by category
                categories = {c["category"]: c["confidence"] for c in classification_result["classifications"]}
                
                # Check that both categories have confidence scores
                assert "indoor" in categories
                assert "outdoor" in categories
                
                # Check that confidence scores are within range
                assert 0 <= categories["indoor"] <= 1
                assert 0 <= categories["outdoor"] <= 1

    @pytest.mark.asyncio
    async def test_classify_invalid_input_path(self, mcp_server: FastMCP):
        """Tests that the tool handles invalid input paths correctly."""
        invalid_path = "/path/to/nonexistent/image.jpg"
        
        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as excinfo:
                await client.call_tool(
                    "classify",
                    {
                        "input_path": invalid_path,
                        "categories": ["indoor", "outdoor"]
                    },
                )
            
            # Check that the error message mentions the file not found
            assert "not found" in str(excinfo.value).lower()

    @pytest.mark.asyncio
    async def test_classify_empty_categories(self, mcp_server: FastMCP, test_images_paths):
        """Tests that the tool handles empty categories list correctly."""
        test_image_path = test_images_paths["outdoor"][0]
        
        # Skip if test image doesn't exist
        if not os.path.exists(test_image_path):
            pytest.skip(f"Test image not found at {test_image_path}")
            
        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as excinfo:
                await client.call_tool(
                    "classify",
                    {
                        "input_path": test_image_path,
                        "categories": []
                    },
                )
            
            # Check that the error message mentions the categories
            assert "categor" in str(excinfo.value).lower()

    @pytest.mark.asyncio
    async def test_classify_custom_categories(self, mcp_server: FastMCP, test_images_paths):
        """Tests the classify tool with custom categories."""
        test_image_path = test_images_paths["outdoor"][0]
        
        # Skip if test image doesn't exist
        if not os.path.exists(test_image_path):
            pytest.skip(f"Test image not found at {test_image_path}")

        custom_categories = ["landscape", "portrait", "abstract", "macro"]
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "classify",
                {
                    "input_path": test_image_path,
                    "categories": custom_categories
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1

            # Parse the result
            classification_result = json.loads(result[0].text)

            # Basic structure checks
            assert "image_path" in classification_result
            assert "classifications" in classification_result
            assert classification_result["image_path"] == test_image_path
            assert isinstance(classification_result["classifications"], list)

            # Check that we have classifications for all custom categories
            assert len(classification_result["classifications"]) == len(custom_categories)
            
            # Check that all categories are present in the results
            result_categories = [c["category"] for c in classification_result["classifications"]]
            for category in custom_categories:
                assert category in result_categories
            
            # Check that confidence scores are within range
            for classification in classification_result["classifications"]:
                assert 0 <= classification["confidence"] <= 1