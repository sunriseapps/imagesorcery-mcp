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
    """Create a colorful test image."""
    img_path = tmp_path / "test_color_image.png"
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    # Add some colors
    img[0:50, 0:50] = [255, 0, 0]  # Blue
    img[0:50, 50:100] = [0, 255, 0]  # Green
    img[50:100, 0:50] = [0, 0, 255]  # Red
    img[50:100, 50:100] = [255, 255, 0]  # Cyan
    cv2.imwrite(str(img_path), img)
    return str(img_path)


class TestChangeColorToolDefinition:
    """Tests for the change_color tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_change_color_in_tools_list(self, mcp_server: FastMCP):
        """Tests that change_color tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            assert tools, "Tools list should not be empty"
            tool_names = [tool.name for tool in tools]
            assert "change_color" in tool_names, "change_color tool should be in the list of available tools"

    @pytest.mark.asyncio
    async def test_change_color_description(self, mcp_server: FastMCP):
        """Tests that change_color tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            change_color_tool = next((tool for tool in tools if tool.name == "change_color"), None)
            assert change_color_tool.description, "change_color tool should have a description"
            assert "color palette" in change_color_tool.description.lower(), "Description should mention changing the color palette"

    @pytest.mark.asyncio
    async def test_change_color_parameters(self, mcp_server: FastMCP):
        """Tests that change_color tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            change_color_tool = next((tool for tool in tools if tool.name == "change_color"), None)

            assert hasattr(change_color_tool, "inputSchema"), "change_color tool should have an inputSchema"
            assert "properties" in change_color_tool.inputSchema, "inputSchema should have properties field"

            required_params = ["input_path", "palette"]
            for param in required_params:
                assert param in change_color_tool.inputSchema["properties"], f"change_color tool should have a '{param}' property in its inputSchema"

            assert "output_path" in change_color_tool.inputSchema["properties"], "change_color tool should have an 'output_path' property in its inputSchema"

            assert change_color_tool.inputSchema["properties"]["input_path"].get("type") == "string"
            assert change_color_tool.inputSchema["properties"]["palette"].get("type") == "string"

            output_path_schema = change_color_tool.inputSchema["properties"]["output_path"]
            assert "anyOf" in output_path_schema
            string_type_present = any(type_option.get("type") == "string" for type_option in output_path_schema["anyOf"])
            assert string_type_present


class TestChangeColorToolExecution:
    """Tests for the change_color tool execution and results."""

    @pytest.mark.asyncio
    async def test_change_color_grayscale(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests the change_color tool with the 'grayscale' palette."""
        output_path = str(tmp_path / "output_grayscale.png")
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "change_color",
                {"input_path": test_image_path, "palette": "grayscale", "output_path": output_path},
            )
            assert len(result) == 1
            assert result[0].text == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
            assert len(img.shape) == 2, "Grayscale image should have 2 dimensions (height, width)"
            
            # Check a pixel from the original blue area
            # Original blue: [255, 0, 0] -> BGR
            # Grayscale conversion: Y = 0.299*R + 0.587*G + 0.114*B = 0.114*255 = 29.07
            # Expected grayscale value: ~29
            pixel_value = img[25, 25]
            assert np.isclose(pixel_value, 29, atol=2), f"Pixel value {pixel_value} is not close to expected grayscale value for blue"
            
            # Check a pixel from the original green area
            # Original green: [0, 255, 0] -> BGR
            # Grayscale conversion: Y = 0.299*R + 0.587*G + 0.114*B = 0.587*255 = 149.69
            # Expected grayscale value: ~150
            pixel_value = img[25, 75]
            assert np.isclose(pixel_value, 150, atol=2), f"Pixel value {pixel_value} is not close to expected grayscale value for green"
    @pytest.mark.asyncio
    async def test_change_color_sepia(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests the change_color tool with the 'sepia' palette."""
        output_path = str(tmp_path / "output_sepia.png")
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "change_color",
                {"input_path": test_image_path, "palette": "sepia", "output_path": output_path},
            )
            assert len(result) == 1
            assert result[0].text == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path)
            assert len(img.shape) == 3, "Sepia image should have 3 dimensions"

            # Check a pixel from the original blue area
            # Original blue: [255, 0, 0] -> BGR
            # Sepia transform: B' = 0.272*B + 0.534*G + 0.131*R = 0.272*255 = 69.36
            #                  G' = 0.349*B + 0.686*G + 0.168*R = 0.349*255 = 88.99
            #                  R' = 0.393*B + 0.769*G + 0.189*R = 0.393*255 = 100.21
            # Expected BGR: [69, 89, 100]
            pixel = img[25, 25]
            assert np.allclose(pixel, [69, 89, 100], atol=2), f"Pixel {pixel} is not close to sepia-toned blue"

    @pytest.mark.asyncio
    async def test_change_color_default_output_path(self, mcp_server: FastMCP, test_image_path):
        """Tests the change_color tool with a default output path."""
        async with Client(mcp_server) as client:
            result = await client.call_tool("change_color", {"input_path": test_image_path, "palette": "grayscale"})
            assert len(result) == 1
            expected_output = test_image_path.replace(".png", "_grayscale.png")
            assert result[0].text == expected_output
            assert os.path.exists(expected_output)

    @pytest.mark.asyncio
    async def test_change_color_invalid_palette(self, mcp_server: FastMCP, test_image_path):
        """Tests the change_color tool with an invalid palette."""
        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as excinfo:
                await client.call_tool("change_color", {"input_path": test_image_path, "palette": "invalid_palette"})
        assert "error calling tool 'change_color'" in str(excinfo.value).lower()