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
    """Create a test image for drawing arrows."""
    img_path = tmp_path / "test_image.png"
    # Create a white image
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(img_path), img)
    return str(img_path)


class TestDrawArrowsToolDefinition:
    """Tests for the draw_arrows tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_draw_arrows_in_tools_list(self, mcp_server: FastMCP):
        """Tests that draw_arrows tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            assert tools, "Tools list should not be empty"
            tool_names = [tool.name for tool in tools]
            assert "draw_arrows" in tool_names, \
                "draw_arrows tool should be in the list of available tools"

    @pytest.mark.asyncio
    async def test_draw_arrows_description(self, mcp_server: FastMCP):
        """Tests that draw_arrows tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            draw_arrows_tool = next((tool for tool in tools if tool.name == "draw_arrows"), None)
            assert draw_arrows_tool.description, "draw_arrows tool should have a description"
            assert "arrow" in draw_arrows_tool.description.lower(), \
                "Description should mention that it draws arrows on an image"

    @pytest.mark.asyncio
    async def test_draw_arrows_parameters(self, mcp_server: FastMCP):
        """Tests that draw_arrows tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            draw_arrows_tool = next((tool for tool in tools if tool.name == "draw_arrows"), None)

            assert hasattr(draw_arrows_tool, "inputSchema"), \
                "draw_arrows tool should have an inputSchema"
            assert "properties" in draw_arrows_tool.inputSchema, \
                "inputSchema should have properties field"

            required_params = ["input_path", "arrows"]
            for param in required_params:
                assert param in draw_arrows_tool.inputSchema["properties"], \
                    f"draw_arrows tool should have a '{param}' property in its inputSchema"

            assert "output_path" in draw_arrows_tool.inputSchema["properties"], \
                "draw_arrows tool should have an 'output_path' property in its inputSchema"

            assert draw_arrows_tool.inputSchema["properties"]["input_path"].get("type") == "string", \
                "input_path should be of type string"
            assert draw_arrows_tool.inputSchema["properties"]["arrows"].get("type") == "array", \
                "arrows should be of type array"
            
            arrows_items_schema = draw_arrows_tool.inputSchema["properties"]["arrows"].get("items", {})
            assert arrows_items_schema.get("type") == "object", "arrows items should be objects"

            output_path_schema = draw_arrows_tool.inputSchema["properties"]["output_path"]
            assert "anyOf" in output_path_schema, "output_path should have anyOf field for optional types"
            string_type_present = any(
                type_option.get("type") == "string" 
                for type_option in output_path_schema["anyOf"]
            )
            assert string_type_present, "output_path should allow string type"


class TestDrawArrowsToolExecution:
    """Tests for the draw_arrows tool execution and results."""

    @pytest.mark.asyncio
    async def test_draw_arrows_tool_execution(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        output_path = str(tmp_path / "output_arrows.png")
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_arrows",
                {
                    "input_path": test_image_path,
                    "arrows": [
                        {"x1": 50, "y1": 50, "x2": 150, "y2": 100, "color": [0, 0, 255], "thickness": 2, "tip_length": 0.2},
                        {"x1": 200, "y1": 150, "x2": 300, "y2": 250, "color": [255, 0, 0], "thickness": 3, "tip_length": 0.15}
                    ],
                    "output_path": output_path,
                },
            )
            assert len(result) == 1
            assert result[0].text == output_path
            assert os.path.exists(output_path)
            img = cv2.imread(output_path)
            assert img.shape[:2] == (300, 400)
            
            # Check if pixels along the arrow path are changed (not white)
            # For the first arrow (red: BGR [0,0,255])
            # Midpoint of the first arrow: ( (50+150)/2, (50+100)/2 ) = (100, 75)
            # Check a pixel near the midpoint
            assert not np.array_equal(img[75, 100], [255, 255, 255]), "First arrow (red) should be drawn"
            
            # For the second arrow (blue: BGR [255,0,0])
            # Midpoint of the second arrow: ( (200+300)/2, (150+250)/2 ) = (250, 200)
            assert not np.array_equal(img[200, 250], [255, 255, 255]), "Second arrow (blue) should be drawn"

    @pytest.mark.asyncio
    async def test_draw_arrows_default_parameters(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        output_path = str(tmp_path / "default_arrows_output.png")
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_arrows",
                {
                    "input_path": test_image_path,
                    "arrows": [{"x1": 10, "y1": 10, "x2": 100, "y2": 100}], # Use default color, thickness, tip_length
                    "output_path": output_path,
                },
            )
            assert len(result) == 1
            assert result[0].text == output_path
            assert os.path.exists(output_path)
            img = cv2.imread(output_path)
            # Check a pixel near the midpoint (55, 55) for default black color [0,0,0]
            # It should not be white [255,255,255]
            assert not np.array_equal(img[55, 55], [255, 255, 255]), "Arrow with default parameters should be drawn"

    @pytest.mark.asyncio
    async def test_draw_arrows_default_output_path(self, mcp_server: FastMCP, test_image_path):
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_arrows",
                {"input_path": test_image_path, "arrows": [{"x1": 20, "y1": 20, "x2": 120, "y2": 120}]},
            )
            assert len(result) == 1
            expected_output = test_image_path.replace(".png", "_with_arrows.png")
            assert result[0].text == expected_output
            assert os.path.exists(expected_output)
            img = cv2.imread(expected_output)
            assert img.shape[:2] == (300, 400)
