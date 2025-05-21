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
    """Create a test image for resizing."""
    img_path = tmp_path / "test_image.png"
    # Create a white image
    img = np.ones((200, 300, 3), dtype=np.uint8) * 255

    # Draw some colored areas to verify resizing
    # Red square (50,50) to (100,100)
    img[50:100, 50:100] = [0, 0, 255]  # OpenCV uses BGR

    # Blue square (100,100) to (150,150)
    img[100:150, 100:150] = [255, 0, 0]  # OpenCV uses BGR

    # Draw a green circle in the center with thickness 5px and diameter 100px
    center = (150, 100)  # x, y coordinates (center of the image)
    radius = 50  # 100px diameter
    color = (0, 255, 0)  # Green in BGR
    thickness = 5
    cv2.circle(img, center, radius, color, thickness)

    # Add text "TEST" in the center
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    text_color = (0, 0, 0)  # Black in BGR
    text_thickness = 2
    text = "TEST"

    # Get text size to center it properly
    text_size = cv2.getTextSize(text, font, font_scale, text_thickness)[0]
    text_x = int(center[0] - text_size[0] / 2)
    text_y = int(center[1] + text_size[1] / 2)

    cv2.putText(
        img, text, (text_x, text_y), font, font_scale, text_color, text_thickness
    )

    cv2.imwrite(str(img_path), img)
    return str(img_path)


class TestResizeToolDefinition:
    """Tests for the resize tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_resize_in_tools_list(self, mcp_server: FastMCP):
        """Tests that resize tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"

            # Check if resize is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "resize" in tool_names, (
                "resize tool should be in the list of available tools"
            )

    @pytest.mark.asyncio
    async def test_resize_description(self, mcp_server: FastMCP):
        """Tests that resize tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            resize_tool = next((tool for tool in tools if tool.name == "resize"), None)

            # Check description
            assert resize_tool.description, "resize tool should have a description"
            assert "resize" in resize_tool.description.lower(), (
                "Description should mention that it resizes an image"
            )

    @pytest.mark.asyncio
    async def test_resize_parameters(self, mcp_server: FastMCP):
        """Tests that resize tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            resize_tool = next((tool for tool in tools if tool.name == "resize"), None)

            # Check input schema
            assert hasattr(resize_tool, "inputSchema"), (
                "resize tool should have an inputSchema"
            )
            assert "properties" in resize_tool.inputSchema, (
                "inputSchema should have properties field"
            )

            # Check required parameters
            assert "input_path" in resize_tool.inputSchema["properties"], (
                "resize tool should have an 'input_path' property in its inputSchema"
            )

            # Check optional parameters
            optional_params = [
                "width",
                "height",
                "scale_factor",
                "interpolation",
                "output_path",
            ]
            for param in optional_params:
                assert param in resize_tool.inputSchema["properties"], (
                    f"resize tool should have a '{param}' property in its inputSchema"
                )

                # Check parameter types - accounting for optional parameters
                # that use anyOf structure
                assert (
                    resize_tool.inputSchema["properties"]["input_path"].get("type")
                    == "string"
                ), "input_path should be of type string"

                # For optional integer parameters, check if they have the correct type
                # in anyOf structure
                for param in ["width", "height"]:
                    param_schema = resize_tool.inputSchema["properties"][param]
                    if "anyOf" in param_schema:
                        # Check if one of the anyOf options is integer
                        has_integer_type = any(
                            option.get("type") == "integer"
                            for option in param_schema["anyOf"]
                        )
                        assert has_integer_type, f"{param} should allow integer type"
                    else:
                        assert param_schema.get("type") == "integer", (
                            f"{param} should be of type integer"
                        )

                # For scale_factor (float parameter)
                scale_factor_schema = resize_tool.inputSchema["properties"][
                    "scale_factor"
                ]
                if "anyOf" in scale_factor_schema:
                    # Check if one of the anyOf options is number
                    has_number_type = any(
                        option.get("type") == "number"
                        for option in scale_factor_schema["anyOf"]
                    )
                    assert has_number_type, "scale_factor should allow number type"
                else:
                    assert scale_factor_schema.get("type") == "number", (
                        "scale_factor should be of type number"
                    )

                # For string parameters
                for param in ["interpolation", "output_path"]:
                    param_schema = resize_tool.inputSchema["properties"][param]
                    if "anyOf" in param_schema:
                        # Check if one of the anyOf options is string
                        has_string_type = any(
                            option.get("type") == "string"
                            for option in param_schema["anyOf"]
                        )
                        assert has_string_type, f"{param} should allow string type"
                    else:
                        assert param_schema.get("type") == "string", (
                            f"{param} should be of type string"
                        )


class TestResizeToolExecution:
    """Tests for the resize tool execution and results."""

    @pytest.mark.asyncio
    async def test_resize_with_dimensions_smaller(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the resize tool execution with specific dimensions (smaller)."""
        output_path = str(tmp_path / "output_dimensions_smaller.png")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "resize",
                {
                    "input_path": test_image_path,
                    "width": 150,
                    "height": 100,
                    "output_path": output_path,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)

            # Verify the resized image dimensions
            img = cv2.imread(output_path)
            assert img.shape[:2] == (100, 150)  # height, width

    @pytest.mark.asyncio
    async def test_resize_with_dimensions_larger(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the resize tool execution with specific dimensions (larger)."""
        output_path = str(tmp_path / "output_dimensions_larger.png")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "resize",
                {
                    "input_path": test_image_path,
                    "width": 600,
                    "height": 400,
                    "output_path": output_path,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)

            # Verify the resized image dimensions
            img = cv2.imread(output_path)
            assert img.shape[:2] == (400, 600)  # height, width

    @pytest.mark.asyncio
    async def test_resize_with_width_only_smaller(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the resize tool execution with only width specified
        (smaller, preserving aspect ratio)."""
        output_path = str(tmp_path / "output_width_only_smaller.png")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "resize",
                {
                    "input_path": test_image_path,
                    "width": 150,
                    "output_path": output_path,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)

            # Verify the resized image dimensions
            img = cv2.imread(output_path)
            assert img.shape[1] == 150  # width
            # Height should be proportional (original: 200x300, new width: 150)
            # So new height should be 200 * (150/300) = 100
            assert img.shape[0] == 100  # height

    @pytest.mark.asyncio
    async def test_resize_with_width_only_larger(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the resize tool execution with only width specified
        (larger, preserving aspect ratio)."""
        output_path = str(tmp_path / "output_width_only_larger.png")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "resize",
                {
                    "input_path": test_image_path,
                    "width": 600,
                    "output_path": output_path,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)

            # Verify the resized image dimensions
            img = cv2.imread(output_path)
            assert img.shape[1] == 600  # width
            # Height should be proportional (original: 200x300, new width: 600)
            # So new height should be 200 * (600/300) = 400
            assert img.shape[0] == 400  # height

    @pytest.mark.asyncio
    async def test_resize_with_height_only_smaller(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the resize tool execution with only height specified
        (smaller, preserving aspect ratio)."""
        output_path = str(tmp_path / "output_height_only_smaller.png")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "resize",
                {
                    "input_path": test_image_path,
                    "height": 100,
                    "output_path": output_path,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)

            # Verify the resized image dimensions
            img = cv2.imread(output_path)
            assert img.shape[0] == 100  # height
            # Width should be proportional (original: 200x300, new height: 100)
            # So new width should be 300 * (100/200) = 150
            assert img.shape[1] == 150  # width

    @pytest.mark.asyncio
    async def test_resize_with_height_only_larger(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the resize tool execution with only height specified
        (larger, preserving aspect ratio)."""
        output_path = str(tmp_path / "output_height_only_larger.png")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "resize",
                {
                    "input_path": test_image_path,
                    "height": 400,
                    "output_path": output_path,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)

            # Verify the resized image dimensions
            img = cv2.imread(output_path)
            assert img.shape[0] == 400  # height
            # Width should be proportional (original: 200x300, new height: 400)
            # So new width should be 300 * (400/200) = 600
            assert img.shape[1] == 600  # width

    @pytest.mark.asyncio
    async def test_resize_with_scale_factor_smaller(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the resize tool execution with scale factor (smaller)."""
        output_path = str(tmp_path / "output_scale_smaller.png")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "resize",
                {
                    "input_path": test_image_path,
                    "scale_factor": 0.5,
                    "output_path": output_path,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)

            # Verify the resized image dimensions
            img = cv2.imread(output_path)
            # Original: 200x300, scale: 0.5, so new dimensions should be 100x150
            assert img.shape[:2] == (100, 150)  # height, width

    @pytest.mark.asyncio
    async def test_resize_with_scale_factor_larger(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the resize tool execution with scale factor (larger)."""
        output_path = str(tmp_path / "output_scale_larger.png")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "resize",
                {
                    "input_path": test_image_path,
                    "scale_factor": 2.0,
                    "output_path": output_path,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)

            # Verify the resized image dimensions
            img = cv2.imread(output_path)
            # Original: 200x300, scale: 2.0, so new dimensions should be 400x600
            assert img.shape[:2] == (400, 600)  # height, width

    @pytest.mark.asyncio
    async def test_resize_default_output_path(
        self, mcp_server: FastMCP, test_image_path
    ):
        """Tests the resize tool with default output path."""
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "resize", {"input_path": test_image_path, "width": 150, "height": 100}
            )

            # Check that the tool returned a result
            assert len(result) == 1
            expected_output = test_image_path.replace(".png", "_resized.png")
            assert result[0].text == expected_output

            # Verify the file exists
            assert os.path.exists(expected_output)

            # Verify the resized image dimensions
            img = cv2.imread(expected_output)
            assert img.shape[:2] == (100, 150)  # height, width

    @pytest.mark.asyncio
    async def test_resize_with_interpolation(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the resize tool with different interpolation methods."""
        interpolation_methods = ["nearest", "linear", "area", "cubic", "lanczos"]

        for method in interpolation_methods:
            # Test downscaling
            output_path_smaller = str(tmp_path / f"output_{method}_smaller.png")

            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "resize",
                    {
                        "input_path": test_image_path,
                        "width": 150,
                        "height": 100,
                        "interpolation": method,
                        "output_path": output_path_smaller,
                    },
                )

                # Check that the tool returned a result
                assert len(result) == 1
                assert result[0].text == output_path_smaller

                # Verify the file exists
                assert os.path.exists(output_path_smaller)

                # Verify the resized image dimensions
                img = cv2.imread(output_path_smaller)
                assert img.shape[:2] == (100, 150)  # height, width

            # Test upscaling
            output_path_larger = str(tmp_path / f"output_{method}_larger.png")

            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "resize",
                    {
                        "input_path": test_image_path,
                        "width": 600,
                        "height": 400,
                        "interpolation": method,
                        "output_path": output_path_larger,
                    },
                )

                # Check that the tool returned a result
                assert len(result) == 1
                assert result[0].text == output_path_larger

                # Verify the file exists
                assert os.path.exists(output_path_larger)

                # Verify the resized image dimensions
                img = cv2.imread(output_path_larger)
                assert img.shape[:2] == (400, 600)  # height, width
