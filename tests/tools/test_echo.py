import pytest
from fastmcp import FastMCP, Client

from imagewizard_mcp.server import mcp as image_wizard_mcp_server

@pytest.fixture
def mcp_server():
    # Use the existing server instance
    return image_wizard_mcp_server

@pytest.mark.asyncio
async def test_echo_tool(mcp_server: FastMCP):
    """Tests the echo tool."""
    async with Client(mcp_server) as client:
        test_text = "Hello, MCP!"
        result = await client.call_tool("echo", {"text": test_text})
        # The tool returns a list of results, we expect one result with the echoed text
        assert len(result) == 1
        assert result[0].text == test_text