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
    """Create a test image with a black and white background for filling."""
    img_path = tmp_path / "test_image.png"
    
    # Create a white image
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    
    # Draw a black rectangle to check blending against
    cv2.rectangle(img, (100, 75), (300, 225), (0, 0, 0), -1)
    
    cv2.imwrite(str(img_path), img)
    return str(img_path)

class TestFillToolDefinition:
    """Tests for the fill tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_fill_in_tools_list(self, mcp_server: FastMCP):
        """Tests that fill tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            assert tools, "Tools list should not be empty"
            tool_names = [tool.name for tool in tools]
            assert "fill" in tool_names, "fill tool should be in the list of available tools"

    @pytest.mark.asyncio
    async def test_fill_description(self, mcp_server: FastMCP):
        """Tests that fill tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            fill_tool = next((tool for tool in tools if tool.name == "fill"), None)
            assert fill_tool.description, "fill tool should have a description"
            assert "fill" in fill_tool.description.lower(), "Description should mention that it fills areas of an image"

    @pytest.mark.asyncio
    async def test_fill_parameters(self, mcp_server: FastMCP):
        """Tests that fill tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            fill_tool = next((tool for tool in tools if tool.name == "fill"), None)
            assert hasattr(fill_tool, "inputSchema"), "fill tool should have an inputSchema"
            assert "properties" in fill_tool.inputSchema, "inputSchema should have properties field"
            required_params = ["input_path", "areas"]
            for param in required_params:
                assert param in fill_tool.inputSchema["properties"], f"fill tool should have a '{param}' property in its inputSchema"
            assert "output_path" in fill_tool.inputSchema["properties"], "fill tool should have an 'output_path' property in its inputSchema"
            assert fill_tool.inputSchema["properties"]["input_path"].get("type") == "string", "input_path should be of type string"
            assert fill_tool.inputSchema["properties"]["areas"].get("type") == "array", "areas should be of type array"
            output_path_schema = fill_tool.inputSchema["properties"]["output_path"]
            assert "anyOf" in output_path_schema, "output_path should have anyOf field for optional types"
            string_type_present = any(type_option.get("type") == "string" for type_option in output_path_schema["anyOf"])
            assert string_type_present, "output_path should allow string type"


class TestFillToolExecution:
    """Tests for the fill tool execution and results."""

    @pytest.mark.asyncio
    async def test_fill_tool_execution(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests the fill tool execution and return value."""
        output_path = str(tmp_path / "output.png")
        
        fill_area = {"x1": 150, "y1": 100, "x2": 250, "y2": 200, "color": [0, 0, 255], "opacity": 0.5}
        
        async with Client(mcp_server) as client:
            result = await client.call_tool("fill", {"input_path": test_image_path, "areas": [fill_area], "output_path": output_path})
            assert len(result) == 1
            assert result[0].text == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path)
            filled_pixel = img[150, 200]
            assert np.allclose(filled_pixel, [0, 0, 128], atol=2)
            unfilled_pixel = img[150, 120]
            assert np.array_equal(unfilled_pixel, [0, 0, 0])
            white_pixel = img[50, 50]
            assert np.array_equal(white_pixel, [255, 255, 255])

    @pytest.mark.asyncio
    async def test_fill_polygon_area(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests the fill tool with a polygon area."""
        output_path = str(tmp_path / "output_poly.png")
        polygon_area = {"polygon": [[160, 110], [240, 110], [200, 190]], "color": [0, 255, 0], "opacity": 0.8}

        async with Client(mcp_server) as client:
            result = await client.call_tool("fill", {"input_path": test_image_path, "areas": [polygon_area], "output_path": output_path})
            assert len(result) == 1
            assert result[0].text == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path)
            poly_center_pixel = img[130, 200]
            assert np.allclose(poly_center_pixel, [0, 204, 0], atol=2)

    @pytest.mark.asyncio
    async def test_fill_default_output_path(self, mcp_server: FastMCP, test_image_path):
        """Tests the fill tool with default output path."""
        async with Client(mcp_server) as client:
            result = await client.call_tool("fill", {"input_path": test_image_path, "areas": [{"x1": 150, "y1": 100, "x2": 250, "y2": 200}]})
            assert len(result) == 1
            expected_output = test_image_path.replace(".png", "_filled.png")
            assert result[0].text == expected_output
            assert os.path.exists(expected_output)

    @pytest.mark.asyncio
    async def test_fill_multiple_areas(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests the fill tool with multiple overlapping areas."""
        output_path = str(tmp_path / "multi_fill.png")
        
        async with Client(mcp_server) as client:
            await client.call_tool("fill", {"input_path": test_image_path, "areas": [{"x1": 110, "y1": 85, "x2": 160, "y2": 135, "color": [0, 0, 255], "opacity": 1.0}, {"x1": 150, "y1": 125, "x2": 200, "y2": 175, "color": [0, 255, 0], "opacity": 0.5}], "output_path": output_path})
            img = cv2.imread(output_path)
            assert np.array_equal(img[100, 120], [0, 0, 255])
            assert np.allclose(img[150, 160], [0, 128, 0], atol=2)
            assert np.allclose(img[130, 155], [0, 128, 128], atol=2)

    @pytest.mark.asyncio
    async def test_fill_transparent_rectangle(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests making a rectangular area transparent."""
        output_path = str(tmp_path / "output_transparent.png")
        fill_area = {"x1": 150, "y1": 100, "x2": 250, "y2": 200, "color": None}

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "fill",
                {
                    "input_path": test_image_path,
                    "areas": [fill_area],
                    "output_path": output_path,
                },
            )
            assert len(result) == 1
            assert result[0].text == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
            assert img.shape[2] == 4  # Should have alpha channel

            # Check a pixel inside the transparent area
            pixel_inside = img[150, 200]
            assert pixel_inside[3] == 0  # Alpha should be 0

            # Check a pixel outside the transparent area
            pixel_outside = img[50, 50]
            assert pixel_outside[3] == 255  # Alpha should be 255

    @pytest.mark.asyncio
    async def test_fill_transparent_polygon(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests making a polygonal area transparent."""
        output_path = str(tmp_path / "output_transparent_poly.png")
        fill_area = {"polygon": [[160, 110], [240, 110], [200, 190]], "color": None}

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "fill",
                {
                    "input_path": test_image_path,
                    "areas": [fill_area],
                    "output_path": output_path,
                },
            )
            assert len(result) == 1
            assert result[0].text == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
            assert img.shape[2] == 4  # Should have alpha channel

            # Check a pixel inside the transparent area (center of the polygon)
            pixel_inside = img[170, 200]
            assert pixel_inside[3] == 0  # Alpha should be 0

            # Check a pixel outside the transparent area
            pixel_outside = img[50, 50]
            assert pixel_outside[3] == 255  # Alpha should be 255
