import os
from pathlib import Path

from fastmcp import FastMCP

# Import the central logger
from imagesorcery_mcp.logging_config import logger
from imagesorcery_mcp.tools import (
    crop,
    detect,
    draw_rectangle,
    draw_text,
    find,
    metainfo,
    models,
    ocr,
    resize,
    rotate,
)

logger.info("Starting 🪄 ImageSorcery MCP server setup")

# Change to project root directory
project_root = Path(__file__).parent.parent.parent
os.chdir(project_root)
logger.info(f"Changed current working directory to: {project_root}")

mcp = FastMCP(
    name="imagesorcery-mcp",
    instructions=(
        "An MCP server providing tools for image processing operations. "
        "Input images must be specified with full paths."
    ),
)
logger.info("FastMCP instance created")

crop.register_tool(mcp)
resize.register_tool(mcp)
rotate.register_tool(mcp)
metainfo.register_tool(mcp)
detect.register_tool(mcp)
find.register_tool(mcp)
models.register_tool(mcp)
draw_text.register_tool(mcp)
draw_rectangle.register_tool(mcp)
ocr.register_tool(mcp)

if __name__ == "__main__":
    mcp.run()
