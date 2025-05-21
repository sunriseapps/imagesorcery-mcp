import json

import cv2
import numpy as np
import pytest
from fastmcp import Client, FastMCP

from imagesorcery_mcp.server import mcp as image_sorcery_mcp_server

# Add this line to filter out the PyTorch warnings
pytestmark = pytest.mark.filterwarnings("ignore:.*'pin_memory' argument is set as true but no accelerator is found.*:UserWarning")


@pytest.fixture
def mcp_server():
    # Use the existing server instance
    return image_sorcery_mcp_server


@pytest.fixture
def test_image_path(tmp_path):
    """Create a test image with text for OCR."""
    img_path = tmp_path / "test_ocr_image.png"
    
    # Create a white image
    img = np.ones((300, 600, 3), dtype=np.uint8) * 255
    
    # Add text to the image
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "Hello World", (50, 50), font, 1, (0, 0, 0), 2)
    cv2.putText(img, "OCR Test", (50, 150), font, 2, (0, 0, 0), 3)
    cv2.putText(img, "12345", (50, 250), font, 1.5, (0, 0, 0), 2)
    
    # Save the image
    cv2.imwrite(str(img_path), img)
    return str(img_path)


class TestOcrToolDefinition:
    """Tests for the OCR tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_ocr_in_tools_list(self, mcp_server: FastMCP):
        """Tests that OCR tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"

            # Check if OCR is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "ocr" in tool_names, (
                "OCR tool should be in the list of available tools"
            )

    @pytest.mark.asyncio
    async def test_ocr_description(self, mcp_server: FastMCP):
        """Tests that OCR tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            ocr_tool = next((tool for tool in tools if tool.name == "ocr"), None)

            # Check description
            assert ocr_tool.description, "OCR tool should have a description"
            assert "ocr" in ocr_tool.description.lower() or "optical character recognition" in ocr_tool.description.lower(), (
                "Description should mention that it performs OCR on an image"
            )

    @pytest.mark.asyncio
    async def test_ocr_parameters(self, mcp_server: FastMCP):
        """Tests that OCR tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            ocr_tool = next((tool for tool in tools if tool.name == "ocr"), None)

            # Check input schema
            assert hasattr(ocr_tool, "inputSchema"), (
                "OCR tool should have an inputSchema"
            )
            assert "properties" in ocr_tool.inputSchema, (
                "inputSchema should have properties field"
            )

            # Check required parameters
            required_params = ["input_path"]
            for param in required_params:
                assert param in ocr_tool.inputSchema["properties"], (
                    f"OCR tool should have a '{param}' property in its inputSchema"
                )

            # Check optional parameters
            optional_params = ["language"]
            for param in optional_params:
                assert param in ocr_tool.inputSchema["properties"], (
                    f"OCR tool should have a '{param}' property in its inputSchema"
                )

            # Check parameter types
            assert (
                ocr_tool.inputSchema["properties"]["input_path"].get("type")
                == "string"
            ), "input_path should be of type string"
            assert (
                ocr_tool.inputSchema["properties"]["language"].get("type")
                == "string"
            ), "language should be of type string"


class TestOcrToolExecution:
    """Tests for the OCR tool execution and results."""

    @pytest.mark.asyncio
    async def test_ocr_tool_execution(self, mcp_server: FastMCP, test_image_path):
        """Tests the OCR tool execution and return value."""
        try:
            import easyocr  # noqa: F401
        except ImportError:
            pytest.skip("EasyOCR is not installed")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "ocr",
                {
                    "input_path": test_image_path,
                    "language": "en",
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1

            # Parse the result
            ocr_result = json.loads(result[0].text)

            # Basic structure checks
            assert "image_path" in ocr_result
            assert "text_segments" in ocr_result
            assert ocr_result["image_path"] == test_image_path
            assert isinstance(ocr_result["text_segments"], list)

            # Check that we have at least some text segments
            assert len(ocr_result["text_segments"]) > 0, (
                "No text segments detected in the test image"
            )

            # Check the structure of a text segment
            segment = ocr_result["text_segments"][0]
            assert "text" in segment, "Text segment should have text content"
            assert "confidence" in segment, "Text segment should have a confidence score"
            assert "bbox" in segment, "Text segment should have a bounding box"

            # Check that the confidence is within expected range
            assert 0 <= segment["confidence"] <= 1, (
                "Confidence should be between 0 and 1"
            )

            # Check that the bounding box has 4 coordinates
            assert len(segment["bbox"]) == 4, "Bounding box should have 4 coordinates"

            # Check for expected text in the image
            # We expect at least one of these texts to be detected
            expected_texts = ["Hello World", "OCR Test", "12345"]
            detected_texts = [segment["text"] for segment in ocr_result["text_segments"]]

            # Check if any of our expected texts are detected (allowing for partial matches)
            matches_found = False
            for expected in expected_texts:
                for detected in detected_texts:
                    if expected.lower() in detected.lower() or detected.lower() in expected.lower():
                        matches_found = True
                        break
                if matches_found:
                    break

            assert matches_found, (
                f"None of the expected texts {expected_texts} were detected. "
                f"Detected texts: {detected_texts}"
            )
