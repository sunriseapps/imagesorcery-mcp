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
    """Create a test image for drawing circles."""
    img_path = tmp_path / "test_image.png"
    # Create a white image
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(img_path), img)
    return str(img_path)


class TestDrawCircleToolDefinition:
    """Tests for the draw_circles tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_draw_circles_in_tools_list(self, mcp_server: FastMCP):
        """Tests that draw_circles tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            assert tools, "Tools list should not be empty"
            tool_names = [tool.name for tool in tools]
            assert "draw_circles" in tool_names, \
                "draw_circles tool should be in the list of available tools"

    @pytest.mark.asyncio
    async def test_draw_circles_description(self, mcp_server: FastMCP):
        """Tests that draw_circles tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            draw_circles_tool = next((tool for tool in tools if tool.name == "draw_circles"), None)
            assert draw_circles_tool.description, "draw_circles tool should have a description"
            assert "circle" in draw_circles_tool.description.lower(), \
                "Description should mention that it draws circles on an image"

    @pytest.mark.asyncio
    async def test_draw_circles_parameters(self, mcp_server: FastMCP):
        """Tests that draw_circles tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            draw_circles_tool = next((tool for tool in tools if tool.name == "draw_circles"), None)

            assert hasattr(draw_circles_tool, "inputSchema"), \
                "draw_circles tool should have an inputSchema"
            assert "properties" in draw_circles_tool.inputSchema, \
                "inputSchema should have properties field"

            required_params = ["input_path", "circles"]
            for param in required_params:
                assert param in draw_circles_tool.inputSchema["properties"], \
                    f"draw_circles tool should have a '{param}' property in its inputSchema"

            assert "output_path" in draw_circles_tool.inputSchema["properties"], \
                "draw_circles tool should have an 'output_path' property in its inputSchema"

            assert draw_circles_tool.inputSchema["properties"]["input_path"].get("type") == "string", \
                "input_path should be of type string"
            assert draw_circles_tool.inputSchema["properties"]["circles"].get("type") == "array", \
                "circles should be of type array"

            circles_items_schema = draw_circles_tool.inputSchema["properties"]["circles"].get("items", {})
            
            # When using a BaseModel for list items, Pydantic generates a $ref
            assert "$ref" in circles_items_schema, "circles items schema should contain a $ref"
            ref_path = circles_items_schema["$ref"]
            
            # Extract the model name from the $ref path
            model_name = ref_path.split("/")[-1]
            
            # Look up the definition in the $defs section
            defs_schema = draw_circles_tool.inputSchema.get("$defs", {})
            assert model_name in defs_schema, f"'$defs' should contain a definition for '{model_name}'"
            
            circle_item_schema = defs_schema[model_name]
            assert circle_item_schema.get("type") == "object", f"Definition for '{model_name}' should be an object"

            circles_props = circle_item_schema.get("properties", {})
            assert "center_x" in circles_props and circles_props["center_x"].get("type") == "integer"
            assert "center_y" in circles_props and circles_props["center_y"].get("type") == "integer"
            assert "radius" in circles_props and circles_props["radius"].get("type") == "integer"
            
            required_circle_item_fields = circle_item_schema.get("required", [])
            assert "center_x" in required_circle_item_fields
            assert "center_y" in required_circle_item_fields
            assert "radius" in required_circle_item_fields

            assert "color" in circles_props, "'color' property should be in circles_props"
            color_schema = circles_props["color"]
            assert "anyOf" in color_schema, "'color' schema should use 'anyOf'"
            
            # Check if one of the anyOf options is an array of integers
            array_of_integers_option_present = any(
                option.get("type") == "array" and 
                option.get("items", {}).get("type") == "integer"
                for option in color_schema["anyOf"]
            )
            assert array_of_integers_option_present, "'color' schema 'anyOf' should include an array of integers"

            assert "thickness" in circles_props, "'thickness' property should be in circles_props"
            thickness_schema = circles_props["thickness"]
            assert "anyOf" in thickness_schema, "'thickness' schema should use 'anyOf'"
            
            # Check if one of the anyOf options is an integer
            integer_option_present = any(
                option.get("type") == "integer"
                for option in thickness_schema["anyOf"]
            )
            assert integer_option_present, "'thickness' schema 'anyOf' should include an integer"

            assert "filled" in circles_props, "'filled' property should be in circles_props"
            filled_schema = circles_props["filled"]
            assert "anyOf" in filled_schema, "'filled' schema should use 'anyOf'"

            # Check if one of the anyOf options is a boolean
            boolean_option_present = any(
                option.get("type") == "boolean"
                for option in filled_schema["anyOf"]
            )
            assert boolean_option_present, "'filled' schema 'anyOf' should include a boolean"

            output_path_schema = draw_circles_tool.inputSchema["properties"]["output_path"]
            assert "anyOf" in output_path_schema, "output_path should have anyOf field for optional types"
            string_type_present = any(
                type_option.get("type") == "string" 
                for type_option in output_path_schema["anyOf"]
            )
            assert string_type_present, "output_path should allow string type"


class TestDrawCircleToolExecution:
    """Tests for the draw_circles tool execution and results."""

    @pytest.mark.asyncio
    async def test_draw_circles_tool_execution(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        output_path = str(tmp_path / "output_circles.png")
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_circles",
                {
                    "input_path": test_image_path,
                    "circles": [
                        {"center_x": 100, "center_y": 100, "radius": 50, "color": [0, 0, 255], "thickness": 2},
                        {"center_x": 250, "center_y": 150, "radius": 30, "color": [255, 0, 0], "thickness": 3}
                    ],
                    "output_path": output_path,
                },
            )
            assert len(result) == 1
            assert result[0].text == output_path
            assert os.path.exists(output_path)
            img = cv2.imread(output_path)
            assert img.shape[:2] == (300, 400)
            assert not np.array_equal(img[100, 150-1], [255, 255, 255]), "Circle 1 (red) should be drawn"
            assert not np.array_equal(img[150, 280-1], [255, 255, 255]), "Circle 2 (blue) should be drawn"

    @pytest.mark.asyncio
    async def test_draw_filled_circle(
        self, mcp_server: FastMCP, test_image_path, tmp_path
    ):
        output_path = str(tmp_path / "filled_circle_output.png")
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_circles",
                {
                    "input_path": test_image_path,
                    "circles": [{"center_x": 150, "center_y": 150, "radius": 50, "color": [0, 255, 0], "filled": True}],
                    "output_path": output_path,
                },
            )
            assert len(result) == 1
            assert result[0].text == output_path
            assert os.path.exists(output_path)
            img = cv2.imread(output_path)
            assert np.array_equal(img[150, 150], [0, 255, 0]), "Circle should be filled with green"
            assert np.array_equal(img[150 + 40, 150 + 0], [0, 255, 0]), "Inner part of filled circle should be green"

    @pytest.mark.asyncio
    async def test_draw_circles_default_output_path(self, mcp_server: FastMCP, test_image_path):
        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "draw_circles",
                {"input_path": test_image_path, "circles": [{"center_x": 50, "center_y": 50, "radius": 20}]},
            )
            assert len(result) == 1
            expected_output = test_image_path.replace(".png", "_with_circles.png")
            assert result[0].text == expected_output
            assert os.path.exists(expected_output)
            img = cv2.imread(expected_output)
            assert img.shape[:2] == (300, 400)
