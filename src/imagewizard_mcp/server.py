import os
from pathlib import Path

from fastmcp import FastMCP

from imagewizard_mcp.tools import (
    crop,
    detect,
    draw_rectangle,
    draw_text,
    find,
    metainfo,
    models,
    resize,
    rotate,
)

# Change to project root directory
os.chdir(Path(__file__).parent.parent.parent)

mcp = FastMCP(
    name="imagewizard-mcp",
    instructions=(
        "An MCP server providing tools for image processing operations. "
        "Input images must be specified with full paths."
    ),
)

crop.register_tool(mcp)
resize.register_tool(mcp)
rotate.register_tool(mcp)
metainfo.register_tool(mcp)
detect.register_tool(mcp)
find.register_tool(mcp)
models.register_tool(mcp)
draw_text.register_tool(mcp)
draw_rectangle.register_tool(mcp)

if __name__ == "__main__":
    mcp.run()
