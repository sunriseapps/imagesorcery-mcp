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
    """Create a test image with a checkerboard pattern for blurring."""
    img_path = tmp_path / "test_image.png"
    
    # Create a white image
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    
    # Create a checkerboard pattern in the center area
    square_size = 20  # Size of each square in the checkerboard
    for i in range(5):  # 5x5 checkerboard
        for j in range(5):
            if (i + j) % 2 == 0:  # Alternate black and white
                x1 = 150 + j * square_size
                y1 = 100 + i * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), -1)  # Black square
    
    cv2.imwrite(str(img_path), img)
    return str(img_path)

class TestBlurToolDefinition:
    """Tests for the blur tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_blur_in_tools_list(self, mcp_server: FastMCP):
        """Tests that blur tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"

            # Check if blur is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "blur" in tool_names, (
                "blur tool should be in the list of available tools"
            )

    @pytest.mark.asyncio
    async def test_blur_description(self, mcp_server: FastMCP):
        """Tests that blur tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            blur_tool = next((tool for tool in tools if tool.name == "blur"), None)

            # Check description
            assert blur_tool.description, "blur tool should have a description"
            assert "blur" in blur_tool.description.lower(), (
                "Description should mention that it blurs areas of an image"
            )

    @pytest.mark.asyncio
    async def test_blur_parameters(self, mcp_server: FastMCP):
        """Tests that blur tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            blur_tool = next((tool for tool in tools if tool.name == "blur"), None)

            # Check input schema
            assert hasattr(blur_tool, "inputSchema"), (
                "blur tool should have an inputSchema"
            )
            assert "properties" in blur_tool.inputSchema, (
                "inputSchema should have properties field"
            )

            # Check required parameters
            required_params = ["input_path", "areas"]
            for param in required_params:
                assert param in blur_tool.inputSchema["properties"], (
                    f"blur tool should have a '{param}' property in its inputSchema"
                )

            # Check optional parameters
            assert "output_path" in blur_tool.inputSchema["properties"], (
                "blur tool should have an 'output_path' property in its inputSchema"
            )

            # Check parameter types
            assert (
                blur_tool.inputSchema["properties"]["input_path"].get("type")
                == "string"
            ), "input_path should be of type string"
            assert (
                blur_tool.inputSchema["properties"]["areas"].get("type")
                == "array"
            ), "areas should be of type array"
            
            # Check output_path type - it can be string or null since it's optional
            output_path_schema = blur_tool.inputSchema["properties"]["output_path"]
            assert "anyOf" in output_path_schema, "output_path should have anyOf field for optional types"
            
            # Check that string is one of the allowed types
            string_type_present = any(
                type_option.get("type") == "string" 
                for type_option in output_path_schema["anyOf"]
            )
            assert string_type_present, "output_path should allow string type"


class TestBlurToolExecution:
    """Tests for the blur tool execution and results."""

    @pytest.mark.asyncio
    async def test_blur_tool_execution(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the blur tool execution and return value."""
        output_path = str(tmp_path / "output.png")
        
        # Define the area to blur - covering the checkerboard pattern
        blur_area = {
            "x1": 150,
            "y1": 100,
            "x2": 250,
            "y2": 200,
            "blur_strength": 21
        }
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "blur",
                {
                    "input_path": test_image_path,
                    "areas": [blur_area],
                    "output_path": output_path,
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)

    @pytest.mark.asyncio
    async def test_blur_polygon_area(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests the blur tool with a polygon area."""
        output_path = str(tmp_path / "output_poly.png")

        # Define a triangular polygon within the checkerboard area
        polygon_area = {
            "polygon": [[160, 110], [240, 110], [200, 190]],
            "blur_strength": 21
        }

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "blur",
                {
                    "input_path": test_image_path,
                    "areas": [polygon_area],
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

            # Verify that the blurred area has different pixel values than the original
            original_img = cv2.imread(test_image_path)

            # Create a mask of the polygon to check pixels
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [np.array(polygon_area["polygon"], dtype=np.int32)], 255)

            # Get pixels from original and blurred images using the mask
            original_pixels = original_img[mask == 255]
            blurred_pixels = img[mask == 255]

            # The pixels should be different
            assert not np.array_equal(original_pixels, blurred_pixels)

            # The standard deviation of the blurred pixels should be lower
            # because the checkerboard pattern is being smoothed
            assert np.std(blurred_pixels) < np.std(original_pixels)

    @pytest.mark.asyncio
    async def test_blur_mixed_areas(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests the blur tool with a mix of rectangle and polygon areas."""
        output_path = str(tmp_path / "output_mixed.png")

        # Define areas
        rect_area = {"x1": 150, "y1": 100, "x2": 250, "y2": 200, "blur_strength": 11}
        poly_area = {"polygon": [[160, 110], [240, 110], [200, 190]], "blur_strength": 21}

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "blur",
                {
                    "input_path": test_image_path,
                    "areas": [rect_area, poly_area],
                    "output_path": output_path,
                },
            )

            assert len(result) == 1
            assert result[0].text == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path)
            original_img = cv2.imread(test_image_path)

            # Check rectangle blur by comparing regions
            blurred_rect_region = img[rect_area["y1"]:rect_area["y2"], rect_area["x1"]:rect_area["x2"]]
            original_rect_region = original_img[rect_area["y1"]:rect_area["y2"], rect_area["x1"]:rect_area["x2"]]
            assert not np.array_equal(blurred_rect_region, original_rect_region)
            assert np.std(blurred_rect_region) < np.std(original_rect_region)

            # Check polygon blur by checking a point inside
            # Create a mask for the polygon to check pixels
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [np.array(poly_area["polygon"], dtype=np.int32)], 255)
            original_poly_pixels = original_img[mask == 255]
            blurred_poly_pixels = img[mask == 255]
            assert not np.array_equal(original_poly_pixels, blurred_poly_pixels)
            assert np.std(blurred_poly_pixels) < np.std(original_poly_pixels)

            # Verify the image was created with correct dimensions
            assert img.shape[:2] == (300, 400)  # height, width

    @pytest.mark.asyncio
    async def test_blur_default_output_path(self, mcp_server: FastMCP, test_image_path):
        """Tests the blur tool with default output path."""
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "blur",
                {
                    "input_path": test_image_path,
                    "areas": [
                        {
                            "x1": 150,
                            "y1": 100,
                            "x2": 250,
                            "y2": 200,
                        }
                    ]
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            expected_output = test_image_path.replace(".png", "_blurred.png")
            assert result[0].text == expected_output

            # Verify the file exists
            assert os.path.exists(expected_output)

    @pytest.mark.asyncio
    async def test_blur_multiple_areas(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests the blur tool with multiple areas."""
        output_path = str(tmp_path / "multi_blur.png")
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "blur",
                {
                    "input_path": test_image_path,
                    "areas": [
                        {
                            "x1": 50,
                            "y1": 50,
                            "x2": 100,
                            "y2": 100,
                            "blur_strength": 11
                        },
                        {
                            "x1": 150,
                            "y1": 100,
                            "x2": 250,
                            "y2": 200,
                            "blur_strength": 21
                        }
                    ],
                    "output_path": output_path
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            assert result[0].text == output_path

            # Verify the file exists
            assert os.path.exists(output_path)