import os
import shutil

import cv2
import numpy as np
import pytest
from fastmcp import Client, FastMCP
from PIL import Image, ImageDraw

from imagesorcery_mcp.server import mcp as image_sorcery_mcp_server


@pytest.fixture
def mcp_server():
    # Use the existing server instance
    return image_sorcery_mcp_server


@pytest.fixture
def test_image_path(tmp_path):
    """Path to a test image with known objects for finding."""
    # Path to the test image in the tests/data directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = os.path.join(os.path.dirname(current_dir), "data")
    src_path = os.path.join(test_data_dir, "test_detection.jpg")
    dest_path = tmp_path / "test_detection.jpg"
    shutil.copy(src_path, dest_path)
    return str(dest_path)


@pytest.fixture
def test_segmentation_image_path(tmp_path):
    """Path to a simple test image for segmentation mask validation."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = os.path.join(os.path.dirname(current_dir), "data")
    src_path = os.path.join(test_data_dir, "test_detection_mask.jpg")
    dest_path = tmp_path / "test_detection_mask.jpg"
    shutil.copy(src_path, dest_path)
    return str(dest_path)


class TestFindToolDefinition:
    """Tests for the find tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_find_in_tools_list(self, mcp_server: FastMCP):
        """Tests that find tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"

            # Check if find is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "find" in tool_names, (
                "find tool should be in the list of available tools"
            )

    @pytest.mark.asyncio
    async def test_find_description(self, mcp_server: FastMCP):
        """Tests that find tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            find_tool = next((tool for tool in tools if tool.name == "find"), None)

            # Check description
            assert find_tool.description, "find tool should have a description"
            assert "find" in find_tool.description.lower(), (
                "Description should mention that it finds objects in an image"
            )

    @pytest.mark.asyncio
    async def test_find_parameters(self, mcp_server: FastMCP):
        """Tests that find tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            find_tool = next((tool for tool in tools if tool.name == "find"), None)

            # Check input schema
            assert hasattr(find_tool, "inputSchema"), (
                "find tool should have an inputSchema"
            )
            assert "properties" in find_tool.inputSchema, (
                "inputSchema should have properties field"
            )

            # Check required parameters
            required_params = ["input_path", "description"]
            for param in required_params:
                assert param in find_tool.inputSchema["properties"], (
                    f"find tool should have a '{param}' property in its inputSchema"
                )

            # Check optional parameters
            optional_params = ["confidence", "model_name", "return_all_matches", "return_geometry", "geometry_format"]
            for param in optional_params:
                assert param in find_tool.inputSchema["properties"], (
                    f"find tool should have a '{param}' property in its inputSchema"
                )

            # Check parameter types and defaults
            assert (
                find_tool.inputSchema["properties"]["input_path"].get("type")
                == "string"
            ), "input_path should be of type string"
            assert (
                find_tool.inputSchema["properties"]["description"].get("type")
                == "string"
            ), "description should be of type string"

            # Check optional parameters (now have anyOf structure with null)
            confidence_schema = find_tool.inputSchema["properties"]["confidence"]
            assert "anyOf" in confidence_schema, "confidence should have anyOf structure for optional parameter"
            assert any(item.get("type") == "number" for item in confidence_schema["anyOf"]), "confidence should allow number type"
            assert any(item.get("type") == "null" for item in confidence_schema["anyOf"]), "confidence should allow null type"

            model_name_schema = find_tool.inputSchema["properties"]["model_name"]
            assert "anyOf" in model_name_schema, "model_name should have anyOf structure for optional parameter"
            assert any(item.get("type") == "string" for item in model_name_schema["anyOf"]), "model_name should allow string type"
            assert any(item.get("type") == "null" for item in model_name_schema["anyOf"]), "model_name should allow null type"
            assert (
                find_tool.inputSchema["properties"]["return_all_matches"].get("type")
                == "boolean"
            ), "return_all_matches should be of type boolean"

            # New parameters for geometry
            assert (
                find_tool.inputSchema["properties"]["return_geometry"].get("type")
                == "boolean"
            ), "return_geometry should be of type boolean"
            assert (
                find_tool.inputSchema["properties"]["return_geometry"].get("default")
                is False
            ), "return_geometry default should be False"

            assert (
                find_tool.inputSchema["properties"]["geometry_format"].get("type")
                == "string"
            ), "geometry_format should be of type string"
            assert (
                find_tool.inputSchema["properties"]["geometry_format"].get("enum")
                == ["mask", "polygon"]
            ), "geometry_format enum should be ['mask', 'polygon']"
            assert (
                find_tool.inputSchema["properties"]["geometry_format"].get("default")
                == "mask"
            ), "geometry_format default should be 'mask'"


class TestFindToolExecution:
    """Tests for the find tool execution and results."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_find_tool_execution(self, mcp_server: FastMCP, test_image_path):
        """Tests the find tool execution and return value."""
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "find",
                {
                    "input_path": test_image_path,
                    "description": "car",
                    "confidence": 0.25,
                    "model_name": "yoloe-11s-seg.pt",
                    "return_all_matches": True,
                },
            )

            # Parse the result
            find_result = result.structured_content

            # Basic structure checks
            assert "image_path" in find_result, "Result should contain image_path"
            assert "query" in find_result, "Result should contain query"
            assert "found_objects" in find_result, "Result should contain found_objects"
            assert "found" in find_result, "Result should contain found flag"
            assert find_result["image_path"] == test_image_path, "Image path should match input path"
            assert find_result["query"] == "car", "Query should match input description"
            assert isinstance(find_result["found_objects"], list), "found_objects should be a list"
            
            # Verify that at least one object was found (the test image has 2 people)
            assert find_result["found"] is True, "Should have found at least one car in the test image"
            assert len(find_result["found_objects"]) > 0, "Should have found at least one car in the test image"
            
            # Check the structure of each found object
            for found_object in find_result["found_objects"]:
                assert "description" in found_object, "Found object should have description"
                assert "match" in found_object, "Found object should have match"
                assert "confidence" in found_object, "Found object should have confidence"
                assert "bbox" in found_object, "Found object should have bbox"
                
                # Check that confidence is within expected range
                assert 0 <= found_object["confidence"] <= 1, "Confidence should be between 0 and 1"
                
                # Check that the bounding box has 4 coordinates
                assert len(found_object["bbox"]) == 4, "Bounding box should have 4 coordinates"
                
                # Check that the description matches the query
                assert found_object["description"] == "car", "Description should match the query"

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_find_single_result(self, mcp_server: FastMCP, test_image_path):
        """Tests that the find tool returns only the best match when return_all_matches is False."""
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "find",
                {
                    "input_path": test_image_path,
                    "description": "car",
                    "confidence": 0.25,
                    "model_name": "yoloe-11s-seg.pt",
                    "return_all_matches": False,
                },
            )

            # Parse the result
            find_result = result.structured_content
            
            # Verify that exactly one car was found when return_all_matches is False
            assert find_result["found"] is True, "Should have found a car in the test image"
            assert len(find_result["found_objects"]) == 1, "Should have returned exactly one car when return_all_matches is False"
            
            # Check the structure of the found object
            found_object = find_result["found_objects"][0]
            assert "description" in found_object, "Found object should have description"
            assert "match" in found_object, "Found object should have match"
            assert "confidence" in found_object, "Found object should have confidence"
            assert "bbox" in found_object, "Found object should have bbox"
            
            # Check that confidence is within expected range
            assert 0 <= found_object["confidence"] <= 1, "Confidence should be between 0 and 1"
            
            # Check that the bounding box has 4 coordinates
            assert len(found_object["bbox"]) == 4, "Bounding box should have 4 coordinates"
            
            # Check that the description matches the query
            assert found_object["description"] == "car", "Description should match the query"
                
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_find_nonexistent_object(self, mcp_server: FastMCP, test_image_path):
        """Tests that the find tool correctly handles searching for objects that don't exist."""
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "find",
                {
                    "input_path": test_image_path,
                    "description": "unicorn",  # Something unlikely to be in the test image
                    "confidence": 0.25,
                    "model_name": "yoloe-11s-seg.pt",
                },
            )

            # Parse the result
            find_result = result.structured_content
            
            # Check the structure of the result
            assert "image_path" in find_result, "Result should contain image_path"
            assert "query" in find_result, "Result should contain query"
            assert "found_objects" in find_result, "Result should contain found_objects"
            assert "found" in find_result, "Result should contain found flag"
            
            # The found flag should be False if no objects were found
            if len(find_result["found_objects"]) == 0:
                assert find_result["found"] is False, "found flag should be False when no objects are found"
            
            # The query should match what we searched for
            assert find_result["query"] == "unicorn", "Query should match input description"

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_find_with_mask_geometry(self, mcp_server: FastMCP, test_image_path):
        """Tests the find tool with mask geometry return."""
        if not os.path.exists(test_image_path):
            pytest.skip(f"Test image not found at {test_image_path}")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "find",
                {
                    "input_path": test_image_path,
                    "description": "car",
                    "model_name": "yoloe-11s-seg.pt",
                    "return_geometry": True,
                    "geometry_format": "mask",
                    "confidence": 0.25,
                },
            )
            find_result = result.structured_content
            assert find_result["found"]
            assert len(find_result["found_objects"]) > 0
            found_object = find_result["found_objects"][0]
            assert "mask_path" in found_object
            assert "polygon" not in found_object
            mask_path = found_object["mask_path"]
            assert isinstance(mask_path, str)
            assert os.path.exists(mask_path)

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_find_with_polygon_geometry(self, mcp_server: FastMCP, test_image_path):
        """Tests the find tool with polygon geometry return."""
        if not os.path.exists(test_image_path):
            pytest.skip(f"Test image not found at {test_image_path}")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "find",
                {
                    "input_path": test_image_path,
                    "description": "car",
                    "model_name": "yoloe-11s-seg.pt",
                    "return_geometry": True,
                    "geometry_format": "polygon",
                    "confidence": 0.25,
                },
            )
            find_result = result.structured_content
            assert find_result["found"]
            assert len(find_result["found_objects"]) > 0
            found_object = find_result["found_objects"][0]
            assert "polygon" in found_object
            assert "mask" not in found_object
            polygon_data = found_object["polygon"]
            assert isinstance(polygon_data, list)
            assert len(polygon_data) > 0
            assert isinstance(polygon_data[0], list)
            assert len(polygon_data[0]) == 2

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_find_no_geometry_by_default(self, mcp_server: FastMCP, test_image_path):
        """Tests that find tool returns no geometry by default."""
        if not os.path.exists(test_image_path):
            pytest.skip(f"Test image not found at {test_image_path}")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "find",
                {
                    "input_path": test_image_path,
                    "description": "car",
                    "model_name": "yoloe-11s-seg.pt",
                    "confidence": 0.25,
                },
            )
            find_result = result.structured_content
            assert find_result["found"]
            assert len(find_result["found_objects"]) > 0
            found_object = find_result["found_objects"][0]
            assert "mask_path" not in found_object
            assert "polygon" not in found_object

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_mask_correctness(self, mcp_server: FastMCP, test_image_path):
        """Tests that returned masks are valid and correctly positioned."""
        with Image.open(test_image_path) as img:
            orig_width, orig_height = img.size

        async with Client(mcp_server) as client:
            result = await client.call_tool("find", {"input_path": test_image_path, "description": "car", "model_name": "yoloe-11s-seg.pt", "return_geometry": True, "geometry_format": "mask", "confidence": 0.25})
            
            find_result = result.structured_content
            assert find_result["found"]
            
            for obj in find_result["found_objects"]:
                assert "mask_path" in obj
                mask_path = obj["mask_path"]
                assert os.path.exists(mask_path)

                mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
                assert mask is not None

                bbox = obj["bbox"]
                x1, y1, x2, y2 = bbox
                
                mask_height, mask_width = mask.shape
                
                assert (
                    (mask_height == mask_width) or
                    (mask_height == orig_height and mask_width == orig_width)
                ), f"Mask dimensions {mask.shape} should be square or match original image"

                scale_x = orig_width / mask_width
                scale_y = orig_height / mask_height

                unique_values = np.unique(mask)
                assert len(unique_values) <= 2
                assert all(v in [0, 255] for v in unique_values)

                assert np.sum(mask) > 0

                mask_indices = np.where(mask > 0)
                if len(mask_indices[0]) > 0:
                    min_y, max_y = mask_indices[0].min(), mask_indices[0].max()
                    min_x, max_x = mask_indices[1].min(), mask_indices[1].max()

                    scaled_x1 = x1 / scale_x
                    scaled_x2 = x2 / scale_x
                    scaled_y1 = y1 / scale_y
                    scaled_y2 = y2 / scale_y

                    tolerance = 10
                    assert min_x >= scaled_x1 - tolerance
                    assert max_x <= scaled_x2 + tolerance
                    assert min_y >= scaled_y1 - tolerance
                    assert max_y <= scaled_y2 + tolerance

                mask_area = np.sum(mask > 0)
                scaled_bbox_area = ((scaled_x2 - scaled_x1) * (scaled_y2 - scaled_y1))
                coverage_ratio = mask_area / scaled_bbox_area if scaled_bbox_area > 0 else 0

                assert 0.1 <= coverage_ratio <= 1.5

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_polygon_correctness(self, mcp_server: FastMCP, test_image_path):
        """Tests that returned polygons are valid and correctly positioned."""
        # Load the test image to get its dimensions
        with Image.open(test_image_path) as img:
            img_width, img_height = img.size

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "find",
                {
                    "input_path": test_image_path,
                    "description": "car",
                    "model_name": "yoloe-11s-seg.pt",
                    "return_geometry": True,
                    "geometry_format": "polygon",
                    "confidence": 0.25,
                },
            )
            
            find_result = result.structured_content
            assert find_result["found"]
            
            for obj in find_result["found_objects"]:
                polygon = obj["polygon"]
                bbox = obj["bbox"]
                x1, y1, x2, y2 = bbox
                
                # 1. Check polygon has at least 3 points
                assert len(polygon) >= 3, "Polygon should have at least 3 points"
                
                # 2. Check all points have exactly 2 coordinates
                for point in polygon:
                    assert len(point) == 2, f"Each polygon point should have 2 coordinates, got {len(point)}"
                
                # 3. Check all coordinates are reasonable
                # Note: Polygon coordinates should be in original image space
                for x, y in polygon:
                    # Allow some tolerance outside image bounds
                    tolerance = 10
                    assert -tolerance <= x <= img_width + tolerance, (
                        f"X coordinate {x} should be within image width {img_width} (with tolerance)"
                    )
                    assert -tolerance <= y <= img_height + tolerance, (
                        f"Y coordinate {y} should be within image height {img_height} (with tolerance)"
                    )
                
                # 4. Check polygon points are within bbox bounds (with tolerance)
                tolerance = 10
                xs = [p[0] for p in polygon]
                ys = [p[1] for p in polygon]
                
                assert min(xs) >= x1 - tolerance, f"Min polygon x {min(xs)} should be >= bbox x1 {x1}"
                assert max(xs) <= x2 + tolerance, f"Max polygon x {max(xs)} should be <= bbox x2 {x2}"
                assert min(ys) >= y1 - tolerance, f"Min polygon y {min(ys)} should be >= bbox y1 {y1}"
                assert max(ys) <= y2 + tolerance, f"Max polygon y {max(ys)} should be <= bbox y2 {y2}"
                
                # 5. Check polygon area is positive (using shoelace formula)
                area = 0
                n = len(polygon)
                for i in range(n):
                    j = (i + 1) % n
                    area += polygon[i][0] * polygon[j][1]
                    area -= polygon[j][0] * polygon[i][1]
                area = abs(area) / 2.0
                
                assert area > 0, "Polygon area should be positive"
                
                # 6. Check polygon area relative to bbox area
                bbox_area = (x2 - x1) * (y2 - y1)
                area_ratio = area / bbox_area
                
                assert 0.1 <= area_ratio <= 1.5, (
                    f"Polygon area ratio {area_ratio:.2f} should be reasonable relative to bbox"
                )

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_mask_to_polygon_consistency(self, mcp_server: FastMCP, test_image_path):
        """Tests that mask and polygon representations are consistent for the same object."""
        with Image.open(test_image_path) as img:
            orig_width, orig_height = img.size
            
        async with Client(mcp_server) as client:
            mask_result = await client.call_tool("find", {"input_path": test_image_path, "description": "car", "model_name": "yoloe-11s-seg.pt", "return_geometry": True, "geometry_format": "mask", "confidence": 0.5, "return_all_matches": False})
            polygon_result = await client.call_tool("find", {"input_path": test_image_path, "description": "car", "model_name": "yoloe-11s-seg.pt", "return_geometry": True, "geometry_format": "polygon", "confidence": 0.5, "return_all_matches": False})
            
            mask_data = mask_result.structured_content
            polygon_data = polygon_result.structured_content
            
            if mask_data["found"] and polygon_data["found"]:
                mask_obj = mask_data["found_objects"][0]
                polygon_obj = polygon_data["found_objects"][0]

                mask_path = mask_obj["mask_path"]
                mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

                mask_bbox = mask_obj["bbox"]
                polygon_bbox = polygon_obj["bbox"]

                bbox_tolerance = 20
                for i in range(4):
                    assert abs(mask_bbox[i] - polygon_bbox[i]) < bbox_tolerance

                polygon_points = polygon_obj["polygon"]
                mask_height, mask_width = mask.shape

                img = Image.new('L', (mask_width, mask_height), 0)

                scale_x = mask_width / orig_width
                scale_y = mask_height / orig_height

                scaled_polygon = [(p[0] * scale_x, p[1] * scale_y) for p in polygon_points]

                ImageDraw.Draw(img).polygon(scaled_polygon, outline=1, fill=1)
                polygon_mask = np.array(img)

                mask_bool = mask > 0
                polygon_mask_bool = polygon_mask > 0
                intersection = np.logical_and(mask_bool, polygon_mask_bool).sum()
                union = np.logical_or(mask_bool, polygon_mask_bool).sum()
                iou = intersection / union if union > 0 else 0

                assert iou > 0.5

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_find_mask_validation_on_simple_image(
        self, mcp_server: FastMCP, test_segmentation_image_path
    ):
        """
        Tests that generated masks from the find tool are valid using a simple image.
        It checks for binarity and bounding box confinement for every generated mask.
        """
        with Image.open(test_segmentation_image_path) as img:
            orig_width, orig_height = img.size

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "find",
                {
                    "input_path": test_segmentation_image_path,
                    "description": "dog",
                    "model_name": "yoloe-11s-seg.pt",
                    "return_geometry": True,
                    "geometry_format": "mask",
                    "confidence": 0.3,
                    "return_all_matches": True,
                },
            )

            find_result = result.structured_content
            assert find_result is not None
            assert find_result["found"], "Should have found a dog in the image"
            assert len(find_result["found_objects"]) >= 1, "Should have found at least one dog"

            # Validate every mask that was generated
            for found_object in find_result["found_objects"]:
                assert "mask_path" in found_object, "Each found object should have a mask_path"
                mask_path = found_object["mask_path"]
                assert os.path.exists(mask_path), f"Mask file should exist at {mask_path}"

                mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
                assert mask is not None, f"Mask file {mask_path} could not be read"

                # 1. Check for binarity (only 0 and 255 values)
                unique_values = np.unique(mask)
                assert all(v in [0, 255] for v in unique_values), (
                    f"Mask {mask_path} is not binary. Found values: {unique_values}"
                )
                assert np.sum(mask) > 0, f"Mask {mask_path} should not be empty"

                # 2. Check for bounding box confinement
                bbox = found_object["bbox"]
                x1, y1, x2, y2 = bbox
                mask_height, mask_width = mask.shape

                scale_x = orig_width / mask_width
                scale_y = orig_height / mask_height

                mask_indices = np.where(mask > 0)
                if len(mask_indices[0]) > 0:
                    min_mask_y, max_mask_y = mask_indices[0].min(), mask_indices[0].max()
                    min_mask_x, max_mask_x = mask_indices[1].min(), mask_indices[1].max()

                    scaled_x1 = x1 / scale_x
                    scaled_y1 = y1 / scale_y
                    scaled_x2 = x2 / scale_x
                    scaled_y2 = y2 / scale_y

                    tolerance = 10
                    assert min_mask_x >= scaled_x1 - tolerance, f"Mask content of {mask_path} extends past the left of its bbox"
                    assert max_mask_x <= scaled_x2 + tolerance, f"Mask content of {mask_path} extends past the right of its bbox"
                    assert min_mask_y >= scaled_y1 - tolerance, f"Mask content of {mask_path} extends past the top of its bbox"
                    assert max_mask_y <= scaled_y2 + tolerance, f"Mask content of {mask_path} extends past the bottom of its bbox"
