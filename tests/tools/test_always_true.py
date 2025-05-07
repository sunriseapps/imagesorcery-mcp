import pytest
from fastmcp import FastMCP, Client

from imagewizard_mcp.server import mcp as image_wizard_mcp_server

@pytest.fixture
def mcp_server():
    # Use the existing server instance
    return image_wizard_mcp_server

@pytest.mark.asyncio
async def test_always_true_tool(mcp_server: FastMCP):
    """Tests the always_true tool."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("always_true")
        # The tool returns a list of results, we expect one result with text 'true'
        assert len(result) == 1
        assert result[0].text == "true"