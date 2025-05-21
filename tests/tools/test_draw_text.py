import os

import cv2
import easyocr
import numpy as np
import pytest
from fastmcp import Client, FastMCP

from imagesorcery_mcp.server import mcp as image_sorcery_mcp_server

# Add this line to filter out the PyTorch warnings
pytestmark = pytest.mark.filterwarnings("ignore:.*'pin_memory' argument is set as true but no accelerator is found.*:UserWarning")

# Initialize the OCR reader for testing
reader = None


def get_ocr_reader():
    """Get or initialize the EasyOCR reader for testing."""
    global reader
    if reader is None:
        reader = easyocr.Reader(['en'])
    return reader


@pytest.fixture
def mcp_server():
    # Use the existing server instance
    return image_sorcery_mcp_server


@pytest.fixture
def test_image_path(tmp_path):
    """Create a test image for drawing text."""
    img_path = tmp_path / "test_image.png"
    # Create a white image
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(img_path), img)
    return str(img_path)


class TestDrawTextsToolDefinition:
    """Tests for the draw_texts tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_draw_texts_in_tools_list(self, mcp_server: FastMCP):
        """Tests that draw_texts tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"

            # Check if draw_texts is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "draw_texts" in tool_names, (
                "draw_texts tool should be in the list of available tools"
            )

    @pytest.mark.asyncio
    async def test_draw_texts_description(self, mcp_server: FastMCP):
        """Tests that draw_texts tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            draw_texts_tool = next((tool for tool in tools if tool.name == "draw_texts"), None)

            # Check description
            assert draw_texts_tool.description, "draw_texts tool should have a description"
            assert "text" in draw_texts_tool.description.lower(), (
                "Description should mention that it draws text on an image"
            )

    @pytest.mark.asyncio
    async def test_draw_texts_parameters(self, mcp_server: FastMCP):
        """Tests that draw_texts tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            draw_texts_tool = next((tool for tool in tools if tool.name == "draw_texts"), None)

            # Check input schema
            assert hasattr(draw_texts_tool, "inputSchema"), (
                "draw_texts tool should have an inputSchema"
            )
            assert "properties" in draw_texts_tool.inputSchema, (
                "inputSchema should have properties field"
            )

            # Check required parameters
            required_params = ["input_path", "texts"]
            for param in required_params:
                assert param in draw_texts_tool.inputSchema["properties"], (
                    f"draw_texts tool should have a '{param}' property in its inputSchema"
                )

            # Check optional parameters
            assert "output_path" in draw_texts_tool.inputSchema["properties"], (
                "draw_texts tool should have an 'output_path' property in its inputSchema"
            )

            # Check parameter types
            assert (
                draw_texts_tool.inputSchema["properties"]["input_path"].get("type")
                == "string"
            ), "input_path should be of type string"
            assert (
                draw_texts_tool.inputSchema["properties"]["texts"].get("type")
                == "array"
            ), "texts should be of type array"
            
            # Check output_path type - it can be string or null since it's optional
            output_path_schema = draw_texts_tool.inputSchema["properties"]["output_path"]
            assert "anyOf" in output_path_schema, "output_path should have anyOf field for optional types"
            
            # Check that string is one of the allowed types
            string_type_present = any(
                type_option.get("type") == "string" 
                for type_option in output_path_schema["anyOf"]
            )
            assert string_type_present, "output_path should allow string type"


class TestDrawTextsToolExecution:
    """Tests for the draw_texts tool execution and results."""

    @pytest.mark.asyncio
    async def test_draw_texts_tool_execution(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        """Tests the draw_texts tool execution and return value."""
        output_path = str(tmp_path / "output.png")
        
        # Define the text to draw
        text1 = "Hello World"
        text2 = "Testing"

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_texts",
                {
                    "input_path": test_image_path,
                    "texts": [
                        {
                            "text": text1,
                            "x": 50,
                            "y": 50,
                            "font_scale": 1.0,
                            "color": [0, 0, 255],  # Red in BGR
                            "thickness": 2
                        },
                        {
                            "text": text2,
                            "x": 100,
                            "y": 150,
                            "font_scale": 2.0,
                            "color": [255, 0, 0],  # Blue in BGR
                            "thickness": 3,
                            "font_face": "FONT_HERSHEY_COMPLEX"
                        }
                    ],
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
            
            # Use OCR to verify the text was actually drawn
            reader = get_ocr_reader()
            ocr_results = reader.readtext(output_path)
            
            # Extract the detected text
            detected_texts = [result[1] for result in ocr_results]
            
            # Check if our drawn texts are detected by OCR
            # We use partial matching because OCR might not be 100% accurate
            assert any(text1 in detected_text for detected_text in detected_texts), \
                f"Expected text '{text1}' not found in OCR results: {detected_texts}"
            assert any(text2 in detected_text for detected_text in detected_texts), \
                f"Expected text '{text2}' not found in OCR results: {detected_texts}"

    @pytest.mark.asyncio
    async def test_draw_texts_default_output_path(self, mcp_server: FastMCP, test_image_path):
        """Tests the draw_texts tool with default output path."""
        # Define the text to draw
        test_text = "Simple Text"
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_texts",
                {
                    "input_path": test_image_path,
                    "texts": [
                        {
                            "text": test_text,
                            "x": 50,
                            "y": 50,
                            "font_scale": 1.5,  # Larger scale for better OCR detection
                            "thickness": 2
                        }
                    ]
                },
            )

            # Check that the tool returned a result
            assert len(result) == 1
            expected_output = test_image_path.replace(".png", "_with_text.png")
            assert result[0].text == expected_output

            # Verify the file exists
            assert os.path.exists(expected_output)
            
            # Use OCR to verify the text was actually drawn
            reader = get_ocr_reader()
            ocr_results = reader.readtext(expected_output)
            
            # Extract the detected text
            detected_texts = [result[1] for result in ocr_results]
            
            # Check if our drawn text is detected by OCR
            assert any(test_text in detected_text for detected_text in detected_texts), \
                f"Expected text '{test_text}' not found in OCR results: {detected_texts}"

    @pytest.mark.asyncio
    async def test_draw_texts_minimal_parameters(self, mcp_server: FastMCP, test_image_path, tmp_path):
        """Tests the draw_texts tool with minimal required parameters."""
        output_path = str(tmp_path / "minimal_output.png")
        
        # Define the text to draw
        test_text = "Minimal Text"
        
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_texts",
                {
                    "input_path": test_image_path,
                    "texts": [
                        {
                            "text": test_text,
                            "x": 50,
                            "y": 50,
                            "font_scale": 1.5,  # Larger scale for better OCR detection
                            "thickness": 2
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
            
            # Use OCR to verify the text was actually drawn
            reader = get_ocr_reader()
            ocr_results = reader.readtext(output_path)
            
            # Extract the detected text
            detected_texts = [result[1] for result in ocr_results]
            
            # Check if our drawn text is detected by OCR
            assert any(test_text in detected_text for detected_text in detected_texts), \
                f"Expected text '{test_text}' not found in OCR results: {detected_texts}"
            assert os.path.exists(output_path)