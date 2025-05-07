from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def echo(text: Annotated[str, Field(description="The text to echo.")]) -> str:
        """Echoes the input text."""
        return text
