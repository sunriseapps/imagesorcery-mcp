import json
from enum import Enum
from typing import Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import BaseModel


class BasicTools(str, Enum):
    ALWAYS_TRUE = "always_true"


class BasicResult(BaseModel):
    result: bool
    message: str


class BasicServer:
    def always_true(self) -> BasicResult:
        """A simple tool that always returns true"""
        return BasicResult(
            result=True,
            message="This tool always returns true",
        )


async def serve() -> None:
    server = Server("mcp-basic")
    basic_server = BasicServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name=BasicTools.ALWAYS_TRUE.value,
                description="A simple tool that always returns true",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls."""
        try:
            match name:
                case BasicTools.ALWAYS_TRUE.value:
                    result = basic_server.always_true()
                case _:
                    raise ValueError(f"Unknown tool: {name}")

            return [
                TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))
            ]

        except Exception as e:
            raise ValueError(f"Error processing request: {str(e)}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)