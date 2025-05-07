import pytest
from fastmcp import Client, FastMCP

from imagewizard_mcp.server import mcp as image_wizard_mcp_server


@pytest.fixture
def mcp_server():
    # Use the existing server instance
    return image_wizard_mcp_server


class TestAlwaysTrueToolDefinition:
    """Tests for the always_true tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_always_true_in_tools_list(self, mcp_server: FastMCP):
        """Tests that always_true tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"

            # Check if always_true is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "always_true" in tool_names, (
                "always_true tool should be in the list of available tools"
            )

    @pytest.mark.asyncio
    async def test_always_true_description(self, mcp_server: FastMCP):
        """Tests that always_true tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            always_true_tool = next(
                (tool for tool in tools if tool.name == "always_true"), None
            )

            # Check description
            assert always_true_tool.description, (
                "always_true tool should have a description"
            )
            assert "always returns true" in always_true_tool.description.lower(), (
                "Description should mention that it always returns true"
            )

    @pytest.mark.asyncio
    async def test_always_true_parameters(self, mcp_server: FastMCP):
        """Tests that always_true tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            always_true_tool = next(
                (tool for tool in tools if tool.name == "always_true"), None
            )

            # Check input schema - this tool should have an empty properties object
            assert hasattr(always_true_tool, "inputSchema"), (
                "always_true tool should have an inputSchema"
            )
            assert "properties" in always_true_tool.inputSchema, (
                "inputSchema should have properties field"
            )
            assert not always_true_tool.inputSchema["properties"], (
                "always_true tool should not have any properties in its inputSchema"
            )


class TestAlwaysTrueToolExecution:
    """Tests for the always_true tool execution and results."""

    @pytest.mark.asyncio
    async def test_always_true_tool_execution(self, mcp_server: FastMCP):
        """Tests the always_true tool execution and return value."""
        async with Client(mcp_server) as client:
            result = await client.call_tool("always_true")
            # The tool returns a list of results, we expect one result with text 'true'
            assert len(result) == 1
            assert result[0].text == "true"
