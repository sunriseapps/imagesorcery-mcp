import pytest
from fastmcp import FastMCP, Client

from imagewizard_mcp.server import mcp as image_wizard_mcp_server

@pytest.fixture
def mcp_server():
    # Use the existing server instance
    return image_wizard_mcp_server


class TestEchoToolDefinition:
    """Tests for the echo tool definition and metadata."""

    @pytest.mark.asyncio
    async def test_echo_in_tools_list(self, mcp_server: FastMCP):
        """Tests that echo tool is in the list of available tools."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            # Verify that tools list is not empty
            assert tools, "Tools list should not be empty"
            
            # Check if echo is in the list of tools
            tool_names = [tool.name for tool in tools]
            assert "echo" in tool_names, "echo tool should be in the list of available tools"

    @pytest.mark.asyncio
    async def test_echo_description(self, mcp_server: FastMCP):
        """Tests that echo tool has the correct description."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            echo_tool = next((tool for tool in tools if tool.name == "echo"), None)
            
            # Check description
            assert echo_tool.description, "echo tool should have a description"
            assert "echo" in echo_tool.description.lower(), "Description should mention that it echoes text"

    @pytest.mark.asyncio
    async def test_echo_parameters(self, mcp_server: FastMCP):
        """Tests that echo tool has the correct parameter structure."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            echo_tool = next((tool for tool in tools if tool.name == "echo"), None)
            
            # Check input schema
            assert hasattr(echo_tool, 'inputSchema'), "echo tool should have an inputSchema"
            assert 'properties' in echo_tool.inputSchema, "inputSchema should have properties field"
            assert 'text' in echo_tool.inputSchema['properties'], "echo tool should have a 'text' property in its inputSchema"
            
            # Check that text property is of type string
            text_property = echo_tool.inputSchema['properties']['text']
            assert text_property.get('type') == 'string', "text property should be of type string"


class TestEchoToolExecution:
    """Tests for the echo tool execution and results."""

    @pytest.mark.asyncio
    async def test_echo_tool_execution(self, mcp_server: FastMCP):
        """Tests the echo tool execution and return value."""
        async with Client(mcp_server) as client:
            test_text = "Hello, MCP!"
            result = await client.call_tool("echo", {"text": test_text})
            # The tool returns a list of results, we expect one result with the echoed text
            assert len(result) == 1
            assert result[0].text == test_text