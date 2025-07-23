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
    """Create a test image for drawing lines."""
    img_path = tmp_path / "test_image.png"
    # Create a white image
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(img_path), img)
    return str(img_path)


class TestDrawLinesToolDefinition:
    """Tests for the draw_lines tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_draw_lines_in_tools_list(self, mcp_server: FastMCP):
        """Tests that draw_lines tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            assert tools, "Tools list should not be empty"
            tool_names = [tool.name for tool in tools]
            assert "draw_lines" in tool_names, \
                "draw_lines tool should be in the list of available tools"

    @pytest.mark.asyncio
    async def test_draw_lines_description(self, mcp_server: FastMCP):
        """Tests that draw_lines tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            draw_lines_tool = next((tool for tool in tools if tool.name == "draw_lines"), None)
            assert draw_lines_tool.description, "draw_lines tool should have a description"
            assert "line" in draw_lines_tool.description.lower(), \
                "Description should mention that it draws lines on an image"

    @pytest.mark.asyncio
    async def test_draw_lines_parameters(self, mcp_server: FastMCP):
        """Tests that draw_lines tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            draw_lines_tool = next((tool for tool in tools if tool.name == "draw_lines"), None)

            assert hasattr(draw_lines_tool, "inputSchema"), \
                "draw_lines tool should have an inputSchema"
            assert "properties" in draw_lines_tool.inputSchema, \
                "inputSchema should have properties field"

            required_params = ["input_path", "lines"]
            for param in required_params:
                assert param in draw_lines_tool.inputSchema["properties"], \
                    f"draw_lines tool should have a '{param}' property in its inputSchema"

            assert "output_path" in draw_lines_tool.inputSchema["properties"], \
                "draw_lines tool should have an 'output_path' property in its inputSchema"

            assert draw_lines_tool.inputSchema["properties"]["input_path"].get("type") == "string", \
                "input_path should be of type string"
            assert draw_lines_tool.inputSchema["properties"]["lines"].get("type") == "array", \
                "lines should be of type array"
            
            lines_items_schema = draw_lines_tool.inputSchema["properties"]["lines"].get("items", {})
            assert lines_items_schema.get("type") == "object", "lines items should be objects"

            output_path_schema = draw_lines_tool.inputSchema["properties"]["output_path"]
            assert "anyOf" in output_path_schema, "output_path should have anyOf field for optional types"
            string_type_present = any(
                type_option.get("type") == "string" 
                for type_option in output_path_schema["anyOf"]
            )
            assert string_type_present, "output_path should allow string type"


class TestDrawLinesToolExecution:
    """Tests for the draw_lines tool execution and results."""

    @pytest.mark.asyncio
    async def test_draw_lines_tool_execution(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        output_path = str(tmp_path / "output_lines.png")
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_lines",
                {
                    "input_path": test_image_path,
                    "lines": [
                        {"x1": 50, "y1": 50, "x2": 150, "y2": 100, "color": [0, 0, 255], "thickness": 2},
                        {"x1": 200, "y1": 150, "x2": 300, "y2": 250, "color": [255, 0, 0], "thickness": 3}
                    ],
                    "output_path": output_path,
                },
            )
            assert result.data == output_path
            assert os.path.exists(output_path)
            img = cv2.imread(output_path)
            assert img.shape[:2] == (300, 400)
            
            # Check if pixels along the line path are changed (not white)
            # For the first line (red: BGR [0,0,255])
            # Midpoint of the first line: ( (50+150)/2, (50+100)/2 ) = (100, 75)
            # Check a pixel near the midpoint
            assert not np.array_equal(img[75, 100], [255, 255, 255]), "First line (red) should be drawn"
            
            # For the second line (blue: BGR [255,0,0])
            # Midpoint of the second line: ( (200+300)/2, (150+250)/2 ) = (250, 200)
            assert not np.array_equal(img[200, 250], [255, 255, 255]), "Second line (blue) should be drawn"

    @pytest.mark.asyncio
    async def test_draw_lines_default_parameters(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        output_path = str(tmp_path / "default_lines_output.png")
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_lines",
                {
                    "input_path": test_image_path,
                    "lines": [{"x1": 10, "y1": 10, "x2": 100, "y2": 100}], # Use default color, thickness
                    "output_path": output_path,
                },
            )
            assert result.data == output_path
            assert os.path.exists(output_path)
            img = cv2.imread(output_path)
            # Check a pixel near the midpoint (55, 55) for default black color [0,0,0]
            # It should not be white [255,255,255]
            assert not np.array_equal(img[55, 55], [255, 255, 255]), "Line with default parameters should be drawn"

    @pytest.mark.asyncio
    async def test_draw_lines_default_output_path(self, mcp_server: FastMCP, test_image_path):
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_lines",
                {"input_path": test_image_path, "lines": [{"x1": 20, "y1": 20, "x2": 120, "y2": 120}]},
            )
            expected_output = test_image_path.replace(".png", "_with_lines.png")
            assert result.data == expected_output
            assert os.path.exists(expected_output)
            img = cv2.imread(expected_output)
            assert img.shape[:2] == (300, 400)
