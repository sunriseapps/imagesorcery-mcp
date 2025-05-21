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
    """Create a test image for drawing rectangles."""
    img_path = tmp_path / "test_image.png"
    # Create a white image
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(img_path), img)
    return str(img_path)


class TestDrawRectanglesToolDefinition:
    """Tests for the draw_rectangles tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_draw_rectangles_in_tools_list(self, mcp_server: FastMCP):
        """Tests that draw_rectangles tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"

            # Check if draw_rectangles is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "draw_rectangles" in tool_names, (
                "draw_rectangles tool should be in the list of available tools"
            )

    @pytest.mark.asyncio
    async def test_draw_rectangles_description(self, mcp_server: FastMCP):
        """Tests that draw_rectangles tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            draw_rectangles_tool = next((tool for tool in tools if tool.name == "draw_rectangles"), None)

            # Check description
            assert draw_rectangles_tool.description, "draw_rectangles tool should have a description"
            assert "rectangle" in draw_rectangles_tool.description.lower(), (
                "Description should mention that it draws rectangles on an image"
            )

    @pytest.mark.asyncio
    async def test_draw_rectangles_parameters(self, mcp_server: FastMCP):
        """Tests that draw_rectangles tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            draw_rectangles_tool = next((tool for tool in tools if tool.name == "draw_rectangles"), None)

            # Check input schema
            assert hasattr(draw_rectangles_tool, "inputSchema"), (
                "draw_rectangles tool should have an inputSchema"
            )
            assert "properties" in draw_rectangles_tool.inputSchema, (
                "inputSchema should have properties field"
            )

            # Check required parameters
            required_params = ["input_path", "rectangles"]
            for param in required_params:
                assert param in draw_rectangles_tool.inputSchema["properties"], (
                    f"draw_rectangles tool should have a '{param}' property in its inputSchema"
                )

            # Check optional parameters
            assert "output_path" in draw_rectangles_tool.inputSchema["properties"], (
                "draw_rectangles tool should have an 'output_path' property in its inputSchema"
            )

            # Check parameter types
            assert (
                draw_rectangles_tool.inputSchema["properties"]["input_path"].get("type")
                == "string"
            ), "input_path should be of type string"
            assert (
                draw_rectangles_tool.inputSchema["properties"]["rectangles"].get("type")
                == "array"
            ), "rectangles should be of type array"
            
            # Check output_path type - it can be string or null since it's optional
            output_path_schema = draw_rectangles_tool.inputSchema["properties"]["output_path"]
            assert "anyOf" in output_path_schema, "output_path should have anyOf field for optional types"
            
            # Check that string is one of the allowed types
            string_type_present = any(
                type_option.get("type") == "string" 
                for type_option in output_path_schema["anyOf"]
            )
            assert string_type_present, "output_path should allow string type"


class TestDrawRectanglesToolExecution:
    """Tests for the draw_rectangles tool execution and results."""

    @pytest.mark.asyncio
    async def test_draw_rectangles_tool_execution(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the draw_rectangles tool execution and return value."""
        output_path = str(tmp_path / "output.png")
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_rectangles",
                {
                    "input_path": test_image_path,
                    "rectangles": [
                        {
                            "x1": 50,
                            "y1": 50,
                            "x2": 150,
                            "y2": 100,
                            "color": [0, 0, 255],  # Red in BGR
                            "thickness": 2
                        },
                        {
                            "x1": 200,
                            "y1": 150,
                            "x2": 300,
                            "y2": 250,
                            "color": [255, 0, 0],  # Blue in BGR
                            "thickness": 3
                        }
                    ],
                    "output_path": output_path,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)

            # Verify the image was created with correct dimensions
            img = cv2.imread(output_path)
            assert img.shape[:2] == (300, 400)  # height, width
            
            # Verify that pixels at rectangle locations have changed color
            # Check a point on the first rectangle's border
            assert not np.array_equal(img[50, 50], [255, 255, 255]), "Rectangle 1 should be drawn"
            
            # Check a point on the second rectangle's border
            assert not np.array_equal(img[150, 200], [255, 255, 255]), "Rectangle 2 should be drawn"

    @pytest.mark.asyncio
    async def test_draw_filled_rectangle(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests drawing a filled rectangle."""
        output_path = str(tmp_path / "filled_output.png")
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_rectangles",
                {
                    "input_path": test_image_path,
                    "rectangles": [
                        {
                            "x1": 100,
                            "y1": 100,
                            "x2": 200,
                            "y2": 200,
                            "color": [0, 255, 0],  # Green in BGR
                            "filled": True
                        }
                    ],
                    "output_path": output_path,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)

            # Verify the image was created with correct dimensions
            img = cv2.imread(output_path)
            
            # Check a point inside the filled rectangle
            # It should be green (BGR: 0, 255, 0)
            assert np.array_equal(img[150, 150], [0, 255, 0]), "Rectangle should be filled with green"

    @pytest.mark.asyncio
    async def test_draw_rectangles_default_output_path(self, mcp_server: FastMCP, test_image_path):
        """Tests the draw_rectangles tool with default output path."""
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_rectangles",
                {
                    "input_path": test_image_path,
                    "rectangles": [
                        {
                            "x1": 50,
                            "y1": 50,
                            "x2": 150,
                            "y2": 100,
                            "color": [0, 0, 0],  # Black in BGR
                            "thickness": 2
                        }
                    ]
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            expected_output = test_image_path.replace(".png", "_with_rectangles.png")
            assert result[0].text == expected_output

            # Verify the file exists
            assert os.path.exists(expected_output)
            
            # Verify the image was created with correct dimensions
            img = cv2.imread(expected_output)
            assert img.shape[:2] == (300, 400)  # height, width