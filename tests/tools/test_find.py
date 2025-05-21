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
    """Path to a test image with known objects for finding."""
    # Path to the test image in the tests/data directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = os.path.join(os.path.dirname(current_dir), "data")
    return os.path.join(test_data_dir, "test_detection.jpg")


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
            optional_params = ["confidence", "model_name", "return_all_matches"]
            for param in optional_params:
                assert param in find_tool.inputSchema["properties"], (
                    f"find tool should have a '{param}' property in its inputSchema"
                )

            # Check parameter types
            assert (
                find_tool.inputSchema["properties"]["input_path"].get("type")
                == "string"
            ), "input_path should be of type string"
            assert (
                find_tool.inputSchema["properties"]["description"].get("type")
                == "string"
            ), "description should be of type string"
            assert (
                find_tool.inputSchema["properties"]["confidence"].get("type")
                == "number"
            ), "confidence should be of type number"
            assert (
                find_tool.inputSchema["properties"]["model_name"].get("type")
                == "string"
            ), "model_name should be of type string"
            assert (
                find_tool.inputSchema["properties"]["return_all_matches"].get("type")
                == "boolean"
            ), "return_all_matches should be of type boolean"


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

            # Check that the tool returned a result
            assert len(result) == 1

            # Parse the result
            find_result = json.loads(result[0].text)

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
            find_result = json.loads(result[0].text)
            
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
            find_result = json.loads(result[0].text)
            
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
