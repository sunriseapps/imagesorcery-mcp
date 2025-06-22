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
def base_image_path(tmp_path):
    """Create a base test image."""
    img_path = tmp_path / "base_image.png"
    # Create a blue image
    img = np.full((300, 400, 3), (255, 0, 0), dtype=np.uint8)
    cv2.imwrite(str(img_path), img)
    return str(img_path)


@pytest.fixture
def overlay_image_path_rgb(tmp_path):
    """Create an RGB overlay image (no alpha)."""
    img_path = tmp_path / "overlay_rgb.png"
    # Create a green square
    img = np.full((100, 100, 3), (0, 255, 0), dtype=np.uint8)
    cv2.imwrite(str(img_path), img)
    return str(img_path)


@pytest.fixture
def overlay_image_path_rgba(tmp_path):
    """Create an RGBA overlay image with transparency."""
    img_path = tmp_path / "overlay_rgba.png"
    # Create a semi-transparent red circle on a transparent background
    img = np.zeros((100, 100, 4), dtype=np.uint8)
    cv2.circle(img, (50, 50), 40, (0, 0, 255, 128), -1)  # B,G,R,A (semi-transparent red)
    cv2.imwrite(str(img_path), img)
    return str(img_path)


class TestOverlayToolDefinition:
    """Tests for the overlay tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_overlay_in_tools_list(self, mcp_server: FastMCP):
        """Tests that overlay tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            assert tools, "Tools list should not be empty"
            tool_names = [tool.name for tool in tools]
            assert "overlay" in tool_names, "overlay tool should be in the list of available tools"

    @pytest.mark.asyncio
    async def test_overlay_parameters(self, mcp_server: FastMCP):
        """Tests that overlay tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            overlay_tool = next((tool for tool in tools if tool.name == "overlay"), None)
            assert overlay_tool is not None

            props = overlay_tool.inputSchema["properties"]
            required = overlay_tool.inputSchema["required"]

            assert "base_image_path" in props and props["base_image_path"]["type"] == "string"
            assert "overlay_image_path" in props and props["overlay_image_path"]["type"] == "string"
            assert "x" in props and props["x"]["type"] == "integer"
            assert "y" in props and props["y"]["type"] == "integer"
            assert "output_path" in props

            assert "base_image_path" in required
            assert "overlay_image_path" in required
            assert "x" in required
            assert "y" in required


class TestOverlayToolExecution:
    """Tests for the overlay tool execution and results."""

    @pytest.mark.asyncio
    async def test_overlay_rgb(self, mcp_server: FastMCP, base_image_path, overlay_image_path_rgb, tmp_path):
        """Tests overlaying an RGB image (no alpha)."""
        output_path = str(tmp_path / "output_rgb.png")
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "overlay",
                {
                    "base_image_path": base_image_path,
                    "overlay_image_path": overlay_image_path_rgb,
                    "x": 50,
                    "y": 50,
                    "output_path": output_path,
                },
            )

            assert len(result) == 1
            assert result[0].text == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path)
            # Check a pixel inside the overlay area, it should be green
            assert np.array_equal(img[100, 100], [0, 255, 0])
            # Check a pixel outside the overlay area, it should be blue
            assert np.array_equal(img[200, 200], [255, 0, 0])

    @pytest.mark.asyncio
    async def test_overlay_rgba(self, mcp_server: FastMCP, base_image_path, overlay_image_path_rgba, tmp_path):
        """Tests overlaying an RGBA image with transparency."""
        output_path = str(tmp_path / "output_rgba.png")
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "overlay",
                {
                    "base_image_path": base_image_path,
                    "overlay_image_path": overlay_image_path_rgba,
                    "x": 50,
                    "y": 50,
                    "output_path": output_path,
                },
            )

            assert len(result) == 1
            assert result[0].text == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path)
            # Check a pixel inside the overlay area, it should be purple
            assert np.allclose(img[100, 100], [128, 0, 128], atol=2)
            # Check a pixel outside the overlay area, it should be blue
            assert np.array_equal(img[55, 55], [255, 0, 0])

    @pytest.mark.asyncio
    async def test_overlay_partial_offscreen(self, mcp_server: FastMCP, base_image_path, overlay_image_path_rgb, tmp_path):
        """Tests overlaying an image partially offscreen."""
        output_path = str(tmp_path / "output_partial.png")
        async with Client(mcp_server) as client:
            await client.call_tool(
                "overlay",
                {
                    "base_image_path": base_image_path,
                    "overlay_image_path": overlay_image_path_rgb,
                    "x": 350,
                    "y": 250,
                    "output_path": output_path,
                },
            )

            assert os.path.exists(output_path)
            img = cv2.imread(output_path)
            # Check a pixel inside the overlay area, it should be green
            assert np.array_equal(img[299, 399], [0, 255, 0])
            # Check a pixel outside the overlay area, it should be blue
            assert np.array_equal(img[299, 349], [255, 0, 0])

    @pytest.mark.asyncio
    async def test_overlay_default_output_path(self, mcp_server: FastMCP, base_image_path, overlay_image_path_rgb):
        """Tests the overlay tool with a default output path."""
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "overlay",
                {
                    "base_image_path": base_image_path,
                    "overlay_image_path": overlay_image_path_rgb,
                    "x": 0,
                    "y": 0,
                },
            )
            assert len(result) == 1
            expected_output = base_image_path.replace(".png", "_overlaid.png")
            assert result[0].text == expected_output
            assert os.path.exists(expected_output)
