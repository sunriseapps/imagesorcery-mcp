import os

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
def test_image_path():
    """Path to a test image with known objects for detection."""
    # Path to the test image in the tests/data directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = os.path.join(os.path.dirname(current_dir), "data")
    return os.path.join(test_data_dir, "test_detection.jpg")


@pytest.fixture
def test_image_negative_path():
    """Path to a test image with different objects for negative testing."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = os.path.join(os.path.dirname(current_dir), "data")
    return os.path.join(test_data_dir, "test_detection_negative.jpg")


class TestDetectToolDefinition:
    """Tests for the detect tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_detect_in_tools_list(self, mcp_server: FastMCP):
        """Tests that detect tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"

            # Check if detect is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "detect" in tool_names, (
                "detect tool should be in the list of available tools"
            )

    @pytest.mark.asyncio
    async def test_detect_description(self, mcp_server: FastMCP):
        """Tests that detect tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            detect_tool = next((tool for tool in tools if tool.name == "detect"), None)

            # Check description
            assert detect_tool.description, "detect tool should have a description"
            assert "detect" in detect_tool.description.lower(), (
                "Description should mention that it detects objects in an image"
            )

    @pytest.mark.asyncio
    async def test_detect_parameters(self, mcp_server: FastMCP):
        """Tests that detect tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            detect_tool = next((tool for tool in tools if tool.name == "detect"), None)

            # Check input schema
            assert hasattr(detect_tool, "inputSchema"), (
                "detect tool should have an inputSchema"
            )
            assert "properties" in detect_tool.inputSchema, (
                "inputSchema should have properties field"
            )

            # Check required parameters
            required_params = ["input_path"]
            for param in required_params:
                assert param in detect_tool.inputSchema["properties"], (
                    f"detect tool should have a '{param}' property in its inputSchema"
                )

            # Check optional parameters
            optional_params = ["confidence", "model_name", "return_geometry", "geometry_format"]
            for param in optional_params:
                assert param in detect_tool.inputSchema["properties"], (
                    f"detect tool should have a '{param}' property in its inputSchema"
                )

            # Check parameter types and defaults
            assert (
                detect_tool.inputSchema["properties"]["input_path"].get("type")
                == "string"
            ), "input_path should be of type string"
            assert (
                detect_tool.inputSchema["properties"]["confidence"].get("type")
                == "number"
            ), "confidence should be of type number"
            assert (
                detect_tool.inputSchema["properties"]["model_name"].get("type")
                == "string"
            ), "model_name should be of type string"
            
            # New parameters for geometry
            assert (
                detect_tool.inputSchema["properties"]["return_geometry"].get("type")
                == "boolean"
            ), "return_geometry should be of type boolean"
            assert (
                detect_tool.inputSchema["properties"]["return_geometry"].get("default")
                is False
            ), "return_geometry default should be False"

            assert (
                detect_tool.inputSchema["properties"]["geometry_format"].get("type")
                == "string"
            ), "geometry_format should be of type string"
            assert (
                detect_tool.inputSchema["properties"]["geometry_format"].get("enum")
                == ["mask", "polygon"]
            ), "geometry_format enum should be ['mask', 'polygon']"
            assert (
                detect_tool.inputSchema["properties"]["geometry_format"].get("default")
                == "mask"
            ), "geometry_format default should be 'mask'"


class TestDetectToolExecution:
    """Tests for the detect tool execution and results."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_detect_tool_execution(self, mcp_server: FastMCP, test_image_path):
        """Tests the detect tool execution and return value."""
        # Skip if test image doesn't exist
        if not os.path.exists(test_image_path):
            pytest.skip(f"Test image not found at {test_image_path}")

        async with Client(mcp_server) as client:
            # Use the smallest model for faster tests
            result = await client.call_tool(
                "detect",
                {
                    "input_path": test_image_path,
                },
            )

            # Parse the result
            detection_result = result.structured_content
            
            # Check that the tool returned a result
            assert detection_result is not None

            # Basic structure checks
            assert "image_path" in detection_result
            assert "detections" in detection_result
            assert detection_result["image_path"] == test_image_path
            assert isinstance(detection_result["detections"], list)

            # Check that we have at least some detections
            assert len(detection_result["detections"]) > 0, (
                "No objects detected in the test image"
            )

            # Check the structure of a detection
            detection = detection_result["detections"][0]
            assert "class" in detection, "Detection should have a class name"
            assert "confidence" in detection, "Detection should have a confidence score"
            assert "bbox" in detection, "Detection should have a bounding box"

            # Check that the confidence is within expected range
            assert 0 <= detection["confidence"] <= 1, (
                "Confidence should be between 0 and 1"
            )

            # Check that the bounding box has 4 coordinates
            assert len(detection["bbox"]) == 4, "Bounding box should have 4 coordinates"

            # Check for expected classes in the image
            # We expect at least one of these classes to be detected
            expected_classes = ["person", "car", "dog"]
            detected_classes = [d["class"] for d in detection_result["detections"]]

            assert any(cls in detected_classes for cls in expected_classes), (
                f"None of the expected classes {expected_classes} were detected. "
                f"Detected classes: {detected_classes}"
            )

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_detect_with_mask_geometry(self, mcp_server: FastMCP, test_image_path):
        """Tests the detect tool with mask geometry return."""
        if not os.path.exists(test_image_path):
            pytest.skip(f"Test image not found at {test_image_path}")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "detect",
                {
                    "input_path": test_image_path,
                    "model_name": "yoloe-11s-seg-pf.pt",
                    "return_geometry": True,
                    "geometry_format": "mask",
                    "confidence": 0.3,
                },
            )
            detection_result = result.structured_content
            assert len(detection_result["detections"]) > 0
            detection = detection_result["detections"][0]
            assert "mask" in detection
            assert "polygon" not in detection
            mask_data = detection["mask"]
            assert isinstance(mask_data, list)
            assert len(mask_data) > 0
            assert isinstance(mask_data[0], list)

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_detect_with_polygon_geometry(self, mcp_server: FastMCP, test_image_path):
        """Tests the detect tool with polygon geometry return."""
        if not os.path.exists(test_image_path):
            pytest.skip(f"Test image not found at {test_image_path}")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "detect",
                {
                    "input_path": test_image_path,
                    "model_name": "yoloe-11s-seg-pf.pt",
                    "return_geometry": True,
                    "geometry_format": "polygon",
                    "confidence": 0.3,
                },
            )
            detection_result = result.structured_content
            assert detection_result is not None
            assert len(detection_result["detections"]) > 0
            detection = detection_result["detections"][0]
            assert "polygon" in detection
            assert "mask" not in detection
            polygon_data = detection["polygon"]
            assert isinstance(polygon_data, list)
            assert len(polygon_data) > 0
            # It's a list of points [x, y]
            assert isinstance(polygon_data[0], list)
            assert len(polygon_data[0]) == 2

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_detect_no_geometry_by_default(self, mcp_server: FastMCP, test_image_path):
        """Tests that no geometry is returned by default."""
        if not os.path.exists(test_image_path):
            pytest.skip(f"Test image not found at {test_image_path}")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "detect",
                {
                    "input_path": test_image_path,
                    "model_name": "yoloe-11s-seg-pf.pt",
                    "confidence": 0.3,
                },
            )
            detection_result = result.structured_content
            assert detection_result is not None
            assert len(detection_result["detections"]) > 0
            detection = detection_result["detections"][0]
            assert "mask" not in detection
            assert "polygon" not in detection

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_detect_geometry_with_non_seg_model_raises_error(
        self, mcp_server: FastMCP, test_image_path, caplog
    ):
        """Tests that requesting geometry with a non-segmentation model raises an error."""
        if not os.path.exists(test_image_path):
            pytest.skip(f"Test image not found at {test_image_path}")

        non_seg_model = "yolov8n.pt"
        model_path = os.path.join("models", non_seg_model)
        if not os.path.exists(model_path):
            pytest.skip(f"Non-segmentation model '{non_seg_model}' not found for testing.")

        async with Client(mcp_server) as client:
            from fastmcp.exceptions import ToolError
            
            with pytest.raises(ToolError):
                await client.call_tool(
                    "detect",
                    {
                        "input_path": test_image_path,
                        "model_name": non_seg_model,
                        "return_geometry": True,
                    },
                )
            
            assert any("does not support segmentation" in record.message for record in caplog.records), \
                "Expected error about segmentation not supported to be logged"
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_detect_negative_scenario(
        self, mcp_server: FastMCP, test_image_negative_path
    ):
        """Tests that certain objects are not detected in an image where they don't
        exist.
        """
        # Skip if test image doesn't exist
        if not os.path.exists(test_image_negative_path):
            pytest.skip(f"Test image not found at {test_image_negative_path}")

        async with Client(mcp_server) as client:
            # Use the smallest model for faster tests
            result = await client.call_tool(
                "detect",
                {
                    "input_path": test_image_negative_path,
                    "confidence": 0.5,
                    "model_name": "yoloe-11s-seg-pf.pt",
                },
            )

            # Parse the result
            detection_result = result.structured_content
            
            # Check that the tool returned a result
            assert detection_result is not None

            # Basic structure checks
            assert "image_path" in detection_result
            assert "detections" in detection_result
            assert detection_result["image_path"] == test_image_negative_path
            assert isinstance(detection_result["detections"], list)

            # Check that we have at least some detections
            assert len(detection_result["detections"]) > 0, (
                "No objects detected in the test image"
            )

            # Objects that should NOT be detected in this image
            not_expected_classes = ["person", "car", "dog", "truck", "bus"]
            detected_classes = [d["class"] for d in detection_result["detections"]]

            # Check that none of the not expected classes are detected
            for cls in not_expected_classes:
                assert cls not in detected_classes, (
                    f"Class '{cls}' was detected but should not be present in the image"
                )

            # Objects that SHOULD be detected in this image
            expected_classes = ["bicycle", "cat"]

            # Check that at least one of the expected classes is detected
            assert any(cls in detected_classes for cls in expected_classes), (
                f"None of the expected classes {expected_classes} were detected. "
                f"Detected classes: {detected_classes}"
            )


class TestDetectGeometryValidation:
    """Tests for validating the correctness of masks and polygons returned by detect tool."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_YOLO_TESTS") == "1",
        reason="Skipping YOLO tests to avoid downloading models in CI",
    )
    async def test_mask_correctness(self, mcp_server: FastMCP, test_image_path):
        """Tests that returned masks are valid and correctly positioned."""
        # Load the test image to get its dimensions
        with Image.open(test_image_path) as img:
            orig_width, orig_height = img.size

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "detect",
                {
                    "input_path": test_image_path,
                    "model_name": "yoloe-11s-seg-pf.pt",
                    "return_geometry": True,
                    "geometry_format": "mask",
                    "confidence": 0.3,
                },
            )
            
            detection_result = result.structured_content
            assert detection_result is not None
            assert len(detection_result["detections"]) > 0
            
            for detection in detection_result["detections"]:
                mask = np.array(detection["mask"])
                bbox = detection["bbox"]
                x1, y1, x2, y2 = bbox
                
                # YOLO typically resizes images to 640x640 for processing
                # So we need to check if the mask dimensions are reasonable
                mask_height, mask_width = mask.shape
                
                # Check that mask dimensions are square (typical for YOLO)
                # or match the original image dimensions
                assert (
                    (mask_height == mask_width) or 
                    (mask_height == orig_height and mask_width == orig_width)
                ), f"Mask dimensions {mask.shape} should be square or match original image"
                
                # Calculate scale factors if mask was resized
                scale_x = orig_width / mask_width
                scale_y = orig_height / mask_height
                
                # Check mask is binary (contains only 0 and 1 or True/False)
                unique_values = np.unique(mask)
                assert len(unique_values) <= 2, "Mask should be binary"
                assert all(v in [0, 1, True, False] for v in unique_values), (
                    "Mask should contain only 0/1 or True/False values"
                )
                
                # Check mask has positive pixels (not empty)
                assert np.sum(mask) > 0, "Mask should not be empty"
                
                # Check mask pixels are within bbox bounds (scaled to mask coordinates)
                mask_indices = np.where(mask > 0)
                if len(mask_indices[0]) > 0:
                    min_y, max_y = mask_indices[0].min(), mask_indices[0].max()
                    min_x, max_x = mask_indices[1].min(), mask_indices[1].max()
                    
                    # Scale bbox to mask coordinates
                    scaled_x1 = x1 / scale_x
                    scaled_x2 = x2 / scale_x
                    scaled_y1 = y1 / scale_y
                    scaled_y2 = y2 / scale_y
                    
                    # Allow some tolerance for segmentation vs bbox differences
                    tolerance = 10
                    assert min_x >= scaled_x1 - tolerance, (
                        f"Mask min_x {min_x} should be >= scaled bbox x1 {scaled_x1} (with tolerance)"
                    )
                    assert max_x <= scaled_x2 + tolerance, (
                        f"Mask max_x {max_x} should be <= scaled bbox x2 {scaled_x2} (with tolerance)"
                    )
                    assert min_y >= scaled_y1 - tolerance, (
                        f"Mask min_y {min_y} should be >= scaled bbox y1 {scaled_y1} (with tolerance)"
                    )
                    assert max_y <= scaled_y2 + tolerance, (
                        f"Mask max_y {max_y} should be <= scaled bbox y2 {scaled_y2} (with tolerance)"
                    )
                
                # Check mask coverage relative to bbox area
                mask_area = np.sum(mask)
                # Scale bbox area to mask resolution
                scaled_bbox_area = ((scaled_x2 - scaled_x1) * (scaled_y2 - scaled_y1))
                coverage_ratio = mask_area / scaled_bbox_area if scaled_bbox_area > 0 else 0
                
                # Mask area should be reasonable relative to bbox (typically 0.3 to 0.9)
                assert 0.1 <= coverage_ratio <= 1.5, (
                    f"Mask coverage ratio {coverage_ratio:.2f} should be reasonable relative to bbox"
                )

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
                "detect",
                {
                    "input_path": test_image_path,
                    "model_name": "yoloe-11s-seg-pf.pt",
                    "return_geometry": True,
                    "geometry_format": "polygon",
                    "confidence": 0.3,
                },
            )
            
            detection_result = result.structured_content
            assert detection_result is not None
            assert len(detection_result["detections"]) > 0
            
            for detection in detection_result["detections"]:
                polygon = detection["polygon"]
                bbox = detection["bbox"]
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
        # Load the test image to get its dimensions
        with Image.open(test_image_path) as img:
            orig_width, orig_height = img.size
            
        async with Client(mcp_server) as client:
            # Get results with mask
            mask_result = await client.call_tool(
                "detect",
                {
                    "input_path": test_image_path,
                    "model_name": "yoloe-11s-seg-pf.pt",
                    "return_geometry": True,
                    "geometry_format": "mask",
                    "confidence": 0.5,  # Higher confidence to get fewer, more reliable results
                },
            )
            
            # Get results with polygon
            polygon_result = await client.call_tool(
                "detect",
                {
                    "input_path": test_image_path,
                    "model_name": "yoloe-11s-seg-pf.pt",
                    "return_geometry": True,
                    "geometry_format": "polygon",
                    "confidence": 0.5,
                },
            )
            
            mask_data = mask_result.structured_content
            assert mask_result is not None
            polygon_data = polygon_result.structured_content
            assert polygon_result is not None
            
            # Get detections for both
            mask_detections = mask_data["detections"]
            polygon_detections = polygon_data["detections"]
            
            # Should have same number of detections
            assert len(mask_detections) == len(polygon_detections), (
                "Should have same number of detections for mask and polygon"
            )
            
            if len(mask_detections) > 0:
                # Sort detections by class and confidence to match them
                mask_detections = sorted(mask_detections, key=lambda x: (x["class"], -x["confidence"]))
                polygon_detections = sorted(polygon_detections, key=lambda x: (x["class"], -x["confidence"]))
                
                # Check first detection of same class
                mask_det = mask_detections[0]
                polygon_det = polygon_detections[0]
                
                # Should be same class
                assert mask_det["class"] == polygon_det["class"], (
                    "First detections should be of same class"
                )
                
                # Check that bboxes are similar (they might differ slightly due to different runs)
                mask_bbox = mask_det["bbox"]
                polygon_bbox = polygon_det["bbox"]
                
                # Allow some tolerance for bbox differences
                bbox_tolerance = 20
                for i in range(4):
                    assert abs(mask_bbox[i] - polygon_bbox[i]) < bbox_tolerance, (
                        "Bounding boxes should be similar for mask and polygon representations"
                    )
                
                # Convert both to same resolution for comparison
                mask = np.array(mask_det["mask"])
                polygon_points = polygon_det["polygon"]
                
                # Determine mask dimensions
                mask_height, mask_width = mask.shape
                
                # Create a mask from the polygon at the same resolution as the returned mask
                img = Image.new('L', (mask_width, mask_height), 0)
                
                # Scale polygon points if needed
                scale_x = mask_width / orig_width
                scale_y = mask_height / orig_height
                
                scaled_polygon = []
                for x, y in polygon_points:
                    scaled_x = x * scale_x
                    scaled_y = y * scale_y
                    scaled_polygon.append((scaled_x, scaled_y))
                
                ImageDraw.Draw(img).polygon(
                    scaled_polygon, 
                    outline=1, 
                    fill=1
                )
                polygon_mask = np.array(img)
                
                # Calculate intersection over union (IoU)
                intersection = np.logical_and(mask, polygon_mask).sum()
                union = np.logical_or(mask, polygon_mask).sum()
                iou = intersection / union if union > 0 else 0
                
                # IoU should be reasonably high for the same object
                # Allow lower threshold as polygon and mask representations can differ
                assert iou > 0.5, (
                    f"Mask and polygon should represent similar regions (IoU: {iou:.2f})"
                )
