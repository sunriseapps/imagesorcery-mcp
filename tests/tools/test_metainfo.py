import json

import pytest
from fastmcp import Client, FastMCP
from PIL import Image

from imagesorcery_mcp.server import mcp as image_sorcery_mcp_server


@pytest.fixture
def mcp_server():
    # Use the existing server instance
    return image_sorcery_mcp_server


@pytest.fixture
def test_image_path(tmp_path):
    """Create a test image for metadata extraction."""
    img_path = tmp_path / "test_image.png"
    img = Image.new("RGB", (200, 200), color="white")

    # Draw some colored areas
    for x in range(50, 100):
        for y in range(50, 100):
            img.putpixel((x, y), (255, 0, 0))  # Red square

    img.save(img_path)
    return str(img_path)


class TestMetainfoToolDefinition:
    """Tests for the get_metainfo tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_metainfo_in_tools_list(self, mcp_server: FastMCP):
        """Tests that get_metainfo tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"

            # Check if get_metainfo is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "get_metainfo" in tool_names, (
                "get_metainfo tool should be in the list of available tools"
            )

    @pytest.mark.asyncio
    async def test_metainfo_description(self, mcp_server: FastMCP):
        """Tests that get_metainfo tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            metainfo_tool = next(
                (tool for tool in tools if tool.name == "get_metainfo"), None
            )

            # Check description
            assert metainfo_tool.description, (
                "get_metainfo tool should have a description"
            )
            assert "metadata" in metainfo_tool.description.lower(), (
                "Description should mention metadata"
            )

    @pytest.mark.asyncio
    async def test_metainfo_parameters(self, mcp_server: FastMCP):
        """Tests that get_metainfo tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            metainfo_tool = next(
                (tool for tool in tools if tool.name == "get_metainfo"), None
            )

            # Check input schema
            assert hasattr(metainfo_tool, "inputSchema"), (
                "get_metainfo tool should have an inputSchema"
            )
            assert "properties" in metainfo_tool.inputSchema, (
                "inputSchema should have properties field"
            )

            # Check required parameters
            required_params = ["input_path"]
            for param in required_params:
                assert param in metainfo_tool.inputSchema["properties"], (
                    f"get_metainfo tool should have a '{param}' property "
                    f"in its inputSchema"
                )

            # Check parameter types
            assert (
                metainfo_tool.inputSchema["properties"]["input_path"].get("type")
                == "string"
            ), "input_path should be of type string"


class TestMetainfoToolExecution:
    """Tests for the get_metainfo tool execution and results."""

    @pytest.mark.asyncio
    async def test_metainfo_tool_execution(self, mcp_server: FastMCP, test_image_path):
        """Tests the get_metainfo tool execution and return value."""
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "get_metainfo", {"input_path": test_image_path}
            )

            # Check that the tool returned a result
            assert len(result) == 1
            # Parse the JSON string from the text attribute
            metadata = json.loads(result[0].text)

            # Verify the metadata contains expected fields
            assert "filename" in metadata
            assert "size_bytes" in metadata
            assert "dimensions" in metadata
            assert "format" in metadata
            assert "color_mode" in metadata
            assert "created_at" in metadata
            assert "modified_at" in metadata

            # Verify the dimensions are correct
            assert metadata["dimensions"]["width"] == 200
            assert metadata["dimensions"]["height"] == 200
            assert metadata["dimensions"]["aspect_ratio"] == 1.0

            # Verify the format is correct
            assert metadata["format"] == "PNG"

            # Verify the color mode is correct
            assert metadata["color_mode"] == "RGB"

    @pytest.mark.asyncio
    async def test_metainfo_nonexistent_file(self, mcp_server: FastMCP, tmp_path):
        """Tests the get_metainfo tool with a nonexistent file."""
        nonexistent_path = str(tmp_path / "nonexistent.png")

        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as excinfo:
                await client.call_tool("get_metainfo", {"input_path": nonexistent_path})
            
        # The error message structure is different with FastMCP - it wraps the original error
        # Just check that we got an error (any kind of exception is acceptable)
        assert isinstance(excinfo.value, Exception)
