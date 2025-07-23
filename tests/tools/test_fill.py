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

@pytest.fixture
def test_jpeg_image_path(tmp_path):
    """Create a test JPEG image (no alpha channel) for testing transparency operations."""
    img_path = tmp_path / "test_image.jpg"
    
    # Create a white image
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    
    # Draw a black rectangle to check blending against
    cv2.rectangle(img, (100, 75), (300, 225), (0, 0, 0), -1)
    
    # Draw a red circle
    cv2.circle(img, (200, 150), 50, (0, 0, 255), -1)
    
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
            assert result.data == output_path
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
            assert result.data == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path)
            poly_center_pixel = img[130, 200]
            assert np.allclose(poly_center_pixel, [0, 204, 0], atol=2)

    @pytest.mark.asyncio
    async def test_fill_default_output_path(self, mcp_server: FastMCP, test_image_path):
        """Tests the fill tool with default output path."""
        async with Client(mcp_server) as client:
            result = await client.call_tool("fill", {"input_path": test_image_path, "areas": [{"x1": 150, "y1": 100, "x2": 250, "y2": 200}]})
            expected_output = test_image_path.replace(".png", "_filled.png")
            assert result.data == expected_output
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
            assert result.data == output_path
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
            assert result.data == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
            assert img.shape[2] == 4  # Should have alpha channel

            # Check a pixel inside the transparent area (center of the polygon)
            pixel_inside = img[170, 200]
            assert pixel_inside[3] == 0  # Alpha should be 0

            # Check a pixel outside the transparent area
            pixel_outside = img[50, 50]
            assert pixel_outside[3] == 255  # Alpha should be 255
    
    @pytest.mark.asyncio
    async def test_fill_invert_rectangle(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests the fill tool with invert_areas for a rectangle."""
        output_path = str(tmp_path / "output_inverted.png")
        
        # Define a rectangle in the center (where the black rectangle is)
        fill_area = {"x1": 150, "y1": 100, "x2": 250, "y2": 200, "color": [0, 255, 0], "opacity": 1.0}
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "fill", 
                {
                    "input_path": test_image_path, 
                    "areas": [fill_area], 
                    "invert_areas": True,
                    "output_path": output_path
                }
            )
            assert result.data == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path)
            
            # Center pixel (inside the specified area) should NOT be filled - remains original
            center_pixel = img[150, 200]
            assert np.array_equal(center_pixel, [0, 0, 0])  # Should remain black (original)
            
            # Pixels outside the area should be filled with green
            outside_pixel = img[50, 50]
            assert np.allclose(outside_pixel, [0, 255, 0], atol=2)  # Should be green - allow tolerance for JPEG
            
            # Another outside pixel
            edge_pixel = img[250, 350]
            assert np.array_equal(edge_pixel, [0, 255, 0])  # Should be green

    @pytest.mark.asyncio
    async def test_fill_invert_polygon(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests the fill tool with invert_areas for a polygon."""
        output_path = str(tmp_path / "output_inverted_poly.png")
        
        # Define a triangle polygon
        polygon_area = {"polygon": [[160, 110], [240, 110], [200, 190]], "color": [255, 0, 0], "opacity": 0.8}
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "fill",
                {
                    "input_path": test_image_path,
                    "areas": [polygon_area],
                    "invert_areas": True,
                    "output_path": output_path
                }
            )
            assert result.data == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path)
            
            # Center of polygon (inside the specified area) should NOT be filled
            poly_center = img[150, 200]
            assert np.array_equal(poly_center, [0, 0, 0])  # Should remain black
            
            # Outside pixels should be filled with blue at 80% opacity
            # Since original is white [255,255,255], and we're applying blue [255,0,0] at 80% opacity:
            # Result = 0.8 * [255,0,0] + 0.2 * [255,255,255] = [255, 51, 51] (approximately)
            outside_pixel = img[50, 50]
            assert np.allclose(outside_pixel, [255, 51, 51], atol=2)  # 80% blue over white

    @pytest.mark.asyncio
    async def test_fill_invert_transparent(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests making everything except a rectangle transparent (background removal)."""
        output_path = str(tmp_path / "output_bg_removed.png")
        
        # Keep only the center rectangle, make everything else transparent
        keep_area = {"x1": 150, "y1": 100, "x2": 250, "y2": 200, "color": None}
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "fill",
                {
                    "input_path": test_image_path,
                    "areas": [keep_area],
                    "invert_areas": True,
                    "output_path": output_path
                }
            )
            assert result.data == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
            assert img.shape[2] == 4  # Should have alpha channel
            
            # Inside the kept area - should be opaque (not modified)
            inside_pixel = img[150, 200]
            assert inside_pixel[3] == 255  # Alpha should be 255 (opaque)
            assert np.array_equal(inside_pixel[:3], [0, 0, 0])  # Color preserved
            
            # Outside the kept area - should be transparent
            outside_pixel = img[50, 50]
            assert outside_pixel[3] == 0  # Alpha should be 0 (transparent)

    @pytest.mark.asyncio
    async def test_fill_invert_multiple_areas(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests invert_areas with multiple areas to keep."""
        output_path = str(tmp_path / "output_multi_keep.png")
        
        # Keep two areas, fill everything else
        areas = [
            {"x1": 50, "y1": 50, "x2": 100, "y2": 100, "color": [0, 0, 255], "opacity": 1.0},
            {"x1": 200, "y1": 150, "x2": 250, "y2": 200}  # Will use first area's color
        ]
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "fill",
                {
                    "input_path": test_image_path,
                    "areas": areas,
                    "invert_areas": True,
                    "output_path": output_path
                }
            )
            assert result.data == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path)
            
            # First kept area should NOT be filled (remains original)
            kept_pixel1 = img[75, 75]
            assert np.array_equal(kept_pixel1, [255, 255, 255])  # Should remain white
            
            # Second kept area should NOT be filled (remains original)
            kept_pixel2 = img[175, 225]
            assert np.array_equal(kept_pixel2, [0, 0, 0])  # Should remain black
            
            # Area between them should be filled with blue
            between_pixel = img[125, 150]
            assert np.array_equal(between_pixel, [0, 0, 255])  # Should be blue (BGR format)

    @pytest.mark.asyncio
    async def test_fill_invert_complex_polygon(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests invert_areas with a complex polygon shape to keep."""
        output_path = str(tmp_path / "output_complex_keep.png")
        
        # Create a star-like polygon
        star_polygon = {
            "polygon": [
                [200, 50], [220, 100], [270, 100], [230, 130],
                [250, 180], [200, 150], [150, 180], [170, 130],
                [130, 100], [180, 100]
            ],
            "color": None  # Make background transparent
        }
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "fill",
                {
                    "input_path": test_image_path,
                    "areas": [star_polygon],
                    "invert_areas": True,
                    "output_path": output_path
                }
            )
            assert result.data == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
            assert img.shape[2] == 4  # Should have alpha channel
            
            # Center of star should be opaque (not modified)
            star_center = img[115, 200]
            assert star_center[3] == 255  # Should be opaque
            
            # Outside corners should be transparent
            corner_pixel = img[10, 10]
            assert corner_pixel[3] == 0  # Should be transparent

    @pytest.mark.asyncio
    async def test_fill_invert_single_area_transparent(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests a simple background removal use case - keep single object, remove background."""
        output_path = str(tmp_path / "object_only.png")
        
        # Define object boundaries
        object_area = {"x1": 100, "y1": 80, "x2": 300, "y2": 220, "color": None}
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "fill",
                {
                    "input_path": test_image_path,
                    "areas": [object_area],
                    "invert_areas": True,
                    "output_path": output_path
                }
            )
            assert result.data == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
            
            # Check that image has alpha channel
            assert img.shape[2] == 4
            
            # Inside object area should be opaque
            object_pixel = img[150, 200]
            assert object_pixel[3] == 255
            
            # Outside object area should be transparent  
            bg_pixel = img[10, 10]
            assert bg_pixel[3] == 0
            
            # Edge case - just outside the object
            edge_pixel = img[79, 150]  # Just above the object
            assert edge_pixel[3] == 0

class TestFillToolWithJPEG:
    """Tests for the fill tool with JPEG images (no alpha channel)."""

    @pytest.mark.asyncio
    async def test_fill_jpeg_to_transparent_rectangle(self, mcp_server: FastMCP, test_jpeg_image_path, tmp_path):
        """Tests making a rectangular area transparent in a JPEG image."""
        output_path = str(tmp_path / "output_transparent.png")  # Output as PNG to support transparency
        fill_area = {"x1": 150, "y1": 100, "x2": 250, "y2": 200, "color": None}

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "fill",
                {
                    "input_path": test_jpeg_image_path,
                    "areas": [fill_area],
                    "output_path": output_path,
                },
            )
            assert result.data == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
            assert img.shape[2] == 4  # Should have alpha channel added

            # Check a pixel inside the transparent area
            pixel_inside = img[150, 200]
            assert pixel_inside[3] == 0  # Alpha should be 0

            # Check a pixel outside the transparent area
            pixel_outside = img[50, 50]
            assert pixel_outside[3] == 255  # Alpha should be 255

    @pytest.mark.asyncio
    async def test_fill_jpeg_invert_transparent(self, mcp_server: FastMCP, test_jpeg_image_path, tmp_path):
        """Tests making everything except a rectangle transparent in a JPEG image (background removal)."""
        output_path = str(tmp_path / "output_bg_removed.png")
        
        # Keep only the center rectangle, make everything else transparent
        keep_area = {"x1": 150, "y1": 100, "x2": 250, "y2": 200, "color": None}
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "fill",
                {
                    "input_path": test_jpeg_image_path,
                    "areas": [keep_area],
                    "invert_areas": True,
                    "output_path": output_path
                }
            )
            assert result.data == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
            assert img.shape[2] == 4  # Should have alpha channel
            
            # Inside the kept area - should be opaque (not modified)
            inside_pixel = img[150, 200]
            assert inside_pixel[3] == 255  # Alpha should be 255 (opaque)
            # Check the red circle is preserved (use allclose due to JPEG compression)
            circle_center = img[150, 200]
            assert circle_center[3] == 255  # Should be opaque
            assert np.allclose(circle_center[:3], [0, 0, 255], atol=2)  # Should be red (BGR) - allow tolerance for JPEG
            
            # Outside the kept area - should be transparent
            outside_pixel = img[50, 50]
            assert outside_pixel[3] == 0  # Alpha should be 0 (transparent)

    @pytest.mark.asyncio
    async def test_fill_jpeg_invert_with_color(self, mcp_server: FastMCP, test_jpeg_image_path, tmp_path):
        """Tests invert_areas with color fill on a JPEG image."""
        output_path = str(tmp_path / "output_inverted_color.jpg")  # Keep as JPEG
        
        # Define a rectangle in the center
        fill_area = {"x1": 150, "y1": 100, "x2": 250, "y2": 200, "color": [0, 255, 0], "opacity": 1.0}
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "fill", 
                {
                    "input_path": test_jpeg_image_path, 
                    "areas": [fill_area], 
                    "invert_areas": True,
                    "output_path": output_path
                }
            )
            assert result.data == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path)
            
            # Center pixel (inside the specified area) should NOT be filled
            center_pixel = img[150, 200]
            assert np.allclose(center_pixel, [0, 0, 255], atol=2)  # Should remain red - allow tolerance for JPEG
            
            # Pixels outside the area should be filled with green
            outside_pixel = img[50, 50]
            assert np.allclose(outside_pixel, [0, 255, 0], atol=2)  # Should be green - allow tolerance for JPEG

    @pytest.mark.asyncio 
    async def test_fill_jpeg_multiple_transparent_areas(self, mcp_server: FastMCP, test_jpeg_image_path, tmp_path):
        """Tests multiple transparent areas on a JPEG image."""
        output_path = str(tmp_path / "output_multi_transparent.png")
        
        areas = [
            {"x1": 50, "y1": 50, "x2": 100, "y2": 100, "color": None},
            {"polygon": [[250, 150], [350, 150], [300, 250]], "color": None}
        ]
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "fill",
                {
                    "input_path": test_jpeg_image_path,
                    "areas": areas,
                    "output_path": output_path
                }
            )
            assert result.data == output_path
            assert os.path.exists(output_path)

            img = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
            assert img.shape[2] == 4  # Should have alpha channel
            
            # First transparent area
            pixel_area1 = img[75, 75]
            assert pixel_area1[3] == 0  # Should be transparent
            
            # Second transparent area (inside polygon)
            pixel_area2 = img[180, 300]
            assert pixel_area2[3] == 0  # Should be transparent
            
            # Non-transparent area
            pixel_normal = img[150, 200]
            assert pixel_normal[3] == 255  # Should be opaque
