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
    """Create a test image for rotation."""
    img_path = tmp_path / "test_image.png"
    # Create a white image
    img = np.ones((100, 200, 3), dtype=np.uint8) * 255

    # Draw a red rectangle in the top-left corner to verify rotation
    # Red rectangle from (10,10) to (40,40)
    img[10:40, 10:40] = [0, 0, 255]  # OpenCV uses BGR

    cv2.imwrite(str(img_path), img)
    return str(img_path)


class TestRotateToolDefinition:
    """Tests for the rotate tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_rotate_in_tools_list(self, mcp_server: FastMCP):
        """Tests that rotate tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"

            # Check if rotate is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "rotate" in tool_names, (
                "rotate tool should be in the list of available tools"
            )

    @pytest.mark.asyncio
    async def test_rotate_description(self, mcp_server: FastMCP):
        """Tests that rotate tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            rotate_tool = next((tool for tool in tools if tool.name == "rotate"), None)

            # Check description
            assert rotate_tool.description, "rotate tool should have a description"
            assert "rotate" in rotate_tool.description.lower(), (
                "Description should mention that it rotates an image"
            )

    @pytest.mark.asyncio
    async def test_rotate_parameters(self, mcp_server: FastMCP):
        """Tests that rotate tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            rotate_tool = next((tool for tool in tools if tool.name == "rotate"), None)

            # Check input schema
            assert hasattr(rotate_tool, "inputSchema"), (
                "rotate tool should have an inputSchema"
            )
            assert "properties" in rotate_tool.inputSchema, (
                "inputSchema should have properties field"
            )

            # Check required parameters
            required_params = ["input_path", "angle"]
            for param in required_params:
                assert param in rotate_tool.inputSchema["properties"], (
                    f"rotate tool should have a '{param}' property in its inputSchema"
                )

            # Check optional parameters
            assert "output_path" in rotate_tool.inputSchema["properties"], (
                "rotate tool should have an 'output_path' property in its inputSchema"
            )

            # Check parameter types
            assert (
                rotate_tool.inputSchema["properties"]["input_path"].get("type")
                == "string"
            ), "input_path should be of type string"
            assert rotate_tool.inputSchema["properties"]["angle"].get("type") in [
                "number",
                "integer",
                "float",
            ], "angle should be a numeric type"
            assert (
                rotate_tool.inputSchema["properties"]["output_path"].get("type")
                == "string"
            ), "output_path should be of type string"


class TestRotateToolExecution:
    """Tests for the rotate tool execution and results."""

    @pytest.mark.asyncio
    async def test_rotate_tool_execution(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the rotate tool execution and return value."""
        output_path = str(tmp_path / "output.png")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "rotate",
                {
                    "input_path": test_image_path,
                    "angle": 90,
                    "output_path": output_path,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)

            # Verify the rotated image dimensions
            original_img = cv2.imread(test_image_path)
            rotated_img = cv2.imread(output_path)

            # For a 90-degree rotation, width and height should be approximately swapped
            # Due to the rotate_bound function, dimensions might be slightly larger
            # to fit the entire rotated image
            # We check that the original width is close to the rotated height
            # and vice versa
            original_height, original_width = original_img.shape[:2]
            rotated_height, rotated_width = rotated_img.shape[:2]

            # Allow for a small margin of error due to padding in rotate_bound
            margin = 5
            assert abs(original_width - rotated_height) <= margin, (
                "Original width should approximately match rotated height "
                "for 90-degree rotation"
            )
            assert abs(original_height - rotated_width) <= margin, (
                "Original height should approximately match rotated width "
                "for 90-degree rotation"
            )

            # Verify the rotation by checking the position of the red rectangle
            # In the original image, the red rectangle is in the top-left corner
            # (10,10) to (40,40)
            # After 90-degree counterclockwise rotation, it should be in the
            # top-right area

            # Check if the top-right area has red pixels (BGR format)
            # For 90-degree counterclockwise rotation, the red rectangle should move
            # from top-left to top-right
            # We need to check the appropriate coordinates in the rotated image

            # The exact coordinates depend on how rotate_bound handles the rotation
            # and padding
            # For a 90-degree counterclockwise rotation of a 100x200 image with a
            # red rectangle at (10,10)-(40,40),
            # the red rectangle should be approximately in the top-right area

            # Check if there are red pixels in the expected area after rotation
            # For 90-degree counterclockwise rotation, the top-left (10,10) would move
            # to approximately (10, rotated_width-40)
            has_red_pixels = False
            for y in range(10, 40):
                for x in range(rotated_width - 40, rotated_width - 10):
                    if x >= 0 and x < rotated_width and y >= 0 and y < rotated_height:
                        # Check if pixel is red (BGR format: [0,0,255])
                        pixel = rotated_img[y, x]
                        if (
                            pixel[0] < 50 and pixel[1] < 50 and pixel[2] > 200
                        ):  # Allow for some color variation
                            has_red_pixels = True
                            break
                if has_red_pixels:
                    break

            assert has_red_pixels, (
                "Red rectangle should be in the top-right area after "
                "90-degree counterclockwise rotation"
            )

    @pytest.mark.asyncio
    async def test_rotate_clockwise(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the rotate tool with clockwise rotation (-90 degrees)."""
        output_path = str(tmp_path / "output_clockwise.png")

        async with Client(mcp_server) as client:
            await client.call_tool(
                "rotate",
                {
                    "input_path": test_image_path,
                    "angle": -90,  # Negative angle for clockwise rotation
                    "output_path": output_path,
                },
            )

            # Verify the file exists
            assert os.path.exists(output_path)

            # Load the rotated image
            rotated_img = cv2.imread(output_path)
            rotated_height, rotated_width = rotated_img.shape[:2]

            # For -90-degree (clockwise) rotation, the red rectangle should move
            # from top-left to bottom-left
            # Check if there are red pixels in the expected area after rotation
            has_red_pixels = False
            for y in range(rotated_height - 40, rotated_height - 10):
                for x in range(10, 40):
                    if x >= 0 and x < rotated_width and y >= 0 and y < rotated_height:
                        # Check if pixel is red (BGR format: [0,0,255])
                        pixel = rotated_img[y, x]
                        if (
                            pixel[0] < 50 and pixel[1] < 50 and pixel[2] > 200
                        ):  # Allow for some color variation
                            has_red_pixels = True
                            break
                if has_red_pixels:
                    break

            assert has_red_pixels, (
                "Red rectangle should be in the bottom-left area after "
                "90-degree clockwise rotation"
            )

    @pytest.mark.asyncio
    async def test_rotate_default_output_path(
        self, mcp_server: FastMCP, test_image_path
    ):
        """Tests the rotate tool with default output path."""
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "rotate", {"input_path": test_image_path, "angle": 45}
            )

            # Check that the tool returned a result
            assert len(result) == 1
            expected_output = test_image_path.replace(".png", "_rotated.png")
            assert result[0].text == expected_output

            # Verify the file exists
            assert os.path.exists(expected_output)
            assert os.path.exists(expected_output)
