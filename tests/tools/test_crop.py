import os

import cv2
import numpy as np
import pytest
from fastmcp import Client, FastMCP

from imagesorcery_mcp.server import mcp as image_sorcery_mcp_server


@pytest.fixture
def mcp_server():
    # Use the existing server instance
    return image_sorcery_mcp_server


@pytest.fixture
def test_image_path(tmp_path):
    """Create a test image for cropping."""
    img_path = tmp_path / "test_image.png"
    # Create a white image
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255

    # Draw some colored areas to verify cropping
    # Red square (50,50) to (100,100)
    img[50:100, 50:100] = [0, 0, 255]  # OpenCV uses BGR

    # Blue square (100,100) to (150,150)
    img[100:150, 100:150] = [255, 0, 0]  # OpenCV uses BGR

    cv2.imwrite(str(img_path), img)
    return str(img_path)


class TestCropToolDefinition:
    """Tests for the crop tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_crop_in_tools_list(self, mcp_server: FastMCP):
        """Tests that crop tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"

            # Check if crop is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "crop" in tool_names, (
                "crop tool should be in the list of available tools"
            )

    @pytest.mark.asyncio
    async def test_crop_description(self, mcp_server: FastMCP):
        """Tests that crop tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            crop_tool = next((tool for tool in tools if tool.name == "crop"), None)

            # Check description
            assert crop_tool.description, "crop tool should have a description"
            assert "crop" in crop_tool.description.lower(), (
                "Description should mention that it crops an image"
            )

    @pytest.mark.asyncio
    async def test_crop_parameters(self, mcp_server: FastMCP):
        """Tests that crop tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            crop_tool = next((tool for tool in tools if tool.name == "crop"), None)

            # Check input schema
            assert hasattr(crop_tool, "inputSchema"), (
                "crop tool should have an inputSchema"
            )
            assert "properties" in crop_tool.inputSchema, (
                "inputSchema should have properties field"
            )

            # Check required parameters
            required_params = ["input_path", "x1", "y1", "x2", "y2"]
            for param in required_params:
                assert param in crop_tool.inputSchema["properties"], (
                    f"crop tool should have a '{param}' property in its inputSchema"
                )

            # Check optional parameters
            assert "output_path" in crop_tool.inputSchema["properties"], (
                "crop tool should have an 'output_path' property in its inputSchema"
            )

            # Check parameter types
            assert (
                crop_tool.inputSchema["properties"]["input_path"].get("type")
                == "string"
            ), "input_path should be of type string"
            assert (
                crop_tool.inputSchema["properties"]["x1"].get("type") == "integer"
            ), "x1 should be of type integer"
            assert (
                crop_tool.inputSchema["properties"]["y1"].get("type") == "integer"
            ), "y1 should be of type integer"
            assert (
                crop_tool.inputSchema["properties"]["x2"].get("type") == "integer"
            ), "x2 should be of type integer"
            assert (
                crop_tool.inputSchema["properties"]["y2"].get("type") == "integer"
            ), "y2 should be of type integer"
            assert (
                crop_tool.inputSchema["properties"]["output_path"].get("type")
                == "string"
            ), "output_path should be of type string"


class TestCropToolExecution:
    """Tests for the crop tool execution and results."""

    @pytest.mark.asyncio
    async def test_crop_tool_execution(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the crop tool execution and return value."""
        output_path = str(tmp_path / "output.png")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "crop",
                {
                    "input_path": test_image_path,
                    "x1": 50,
                    "y1": 50,
                    "x2": 100,
                    "y2": 100,
                    "output_path": output_path,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)

            # Verify the cropped image dimensions
            img = cv2.imread(output_path)
            assert img.shape[:2] == (50, 50)  # height, width
            # Check if the red square was properly cropped (BGR in OpenCV)
            assert all(img[0, 0] == [0, 0, 255])  # Red in BGR

    @pytest.mark.asyncio
    async def test_crop_default_output_path(self, mcp_server: FastMCP, test_image_path):
        """Tests the crop tool with default output path."""
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "crop",
                {
                    "input_path": test_image_path,
                    "x1": 50,
                    "y1": 50,
                    "x2": 100,
                    "y2": 100,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            expected_output = test_image_path.replace(".png", "_cropped.png")
            assert result[0].text == expected_output

            # Verify the file exists
            assert os.path.exists(expected_output)
