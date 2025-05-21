import argparse
import os
import sys
from pathlib import Path

from fastmcp import FastMCP

# Import the central logger
from imagesorcery_mcp.logging_config import logger
from imagesorcery_mcp.tools import (
    blur,
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

# Create a module-level mcp instance for backward compatibility with tests
mcp = FastMCP(
    name="imagesorcery-mcp",
    instructions=(
        "An MCP server providing tools for image processing operations. "
        "Input images must be specified with full paths."
    ),
)

# Register tools with the module-level mcp instance
blur.register_tool(mcp)
crop.register_tool(mcp)
detect.register_tool(mcp)
draw_rectangle.register_tool(mcp)
draw_text.register_tool(mcp)
find.register_tool(mcp)
metainfo.register_tool(mcp)
models.register_tool(mcp)
ocr.register_tool(mcp)
resize.register_tool(mcp)
rotate.register_tool(mcp)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ImageSorcery MCP Server")
    parser.add_argument(
        "--post-install", 
        action="store_true", 
        help="Run post-installation tasks and exit"
    )
    return parser.parse_args()

def main():
    """Main entry point for the server."""
    args = parse_arguments()
    
    logger.info("Starting 🪄 ImageSorcery MCP server setup")
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent.parent

    # Read version from pyproject.toml and print it
    try:
        import toml
        with open(project_root / "pyproject.toml", "r") as f:
            pyproject_data = toml.load(f)
        version = pyproject_data.get("project", {}).get("version", "N/A")
        print(f"ImageSorcery MCP Version: {version}")
    except Exception as e:
        logger.error(f"Could not read version from pyproject.toml: {e}")

    os.chdir(project_root)
    logger.info(f"Changed current working directory to: {project_root}")
    
    # If --post-install flag is provided, run post-installation tasks and exit
    if args.post_install:
        logger.info("Post-installation flag detected, running post-installation tasks")
        try:
            from imagesorcery_mcp.scripts.post_install import run_post_install
            success = run_post_install()
            if not success:
                logger.error("Post-installation tasks failed")
                sys.exit(1)
            logger.info("Post-installation tasks completed successfully")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error during post-installation: {str(e)}")
            sys.exit(1)
    
    # For actual server execution, we'll use the global mcp instance
    logger.info("Starting MCP server")
    mcp.run()

if __name__ == "__main__":
    main()
