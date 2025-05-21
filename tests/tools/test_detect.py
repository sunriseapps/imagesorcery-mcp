import json
import os

import pytest
from fastmcp import Client, FastMCP

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
            optional_params = ["confidence", "model_name"]
            for param in optional_params:
                assert param in detect_tool.inputSchema["properties"], (
                    f"detect tool should have a '{param}' property in its inputSchema"
                )

            # Check parameter types
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

            # Check that the tool returned a result
            assert len(result) == 1

            # Parse the result
            detection_result = json.loads(result[0].text)

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

            # Check that the tool returned a result
            assert len(result) == 1

            # Parse the result
            detection_result = json.loads(result[0].text)

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
