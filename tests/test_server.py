import pytest
from fastmcp import Client, FastMCP

from imagesorcery_mcp.server import mcp as image_sorcery_mcp_server


@pytest.fixture
def mcp_server():
    # Use the existing server instance
    return image_sorcery_mcp_server


@pytest.mark.asyncio
async def test_list_tools(mcp_server: FastMCP):
    """Tests listing available tools."""
    async with Client(mcp_server) as client:
        tools = await client.list_tools()  # Correctly list tools using the client

        # Verify that tools list is not empty
        assert tools, "Tools list should not be empty"
        assert len(tools) > 0, "Tools list should contain at least one tool"


@pytest.mark.asyncio
async def test_nonexisting_tool(mcp_server: FastMCP):
    """Tests calling a non-existent tool."""
    nonexistent_tool_name = "nonexistent_tool"

    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as excinfo:
            await client.call_tool(nonexistent_tool_name)

        # Check that the error message contains the tool name
        assert nonexistent_tool_name in str(excinfo.value)
