import argparse
import os
import sys
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware

from imagesorcery_mcp.logging_config import logger

# Change to project root directory
project_root = Path(__file__).parent.parent.parent
os.chdir(project_root)
logger.info(f"Changed current working directory to: {project_root}")

# Load environment variables from .env if python-dotenv is available (so handlers see keys on import)
try:
    from dotenv import load_dotenv  # type: ignore
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        logger.info(f"Loaded environment variables from: {env_file}")
    else:
        logger.debug(".env file not found, skipping dotenv loading")
except Exception:
    logger.debug("python-dotenv not available, skipping .env loading")

from imagesorcery_mcp.middlewares.telemetry import TelemetryMiddleware  # noqa: E402
from imagesorcery_mcp.middlewares.validation import (  # noqa: E402
    ImprovedValidationMiddleware,  # noqa: E402
)
from imagesorcery_mcp.prompts import remove_background  # noqa: E402
from imagesorcery_mcp.resources import models  # noqa: E402
from imagesorcery_mcp.tools import (  # noqa: E402
    blur,
    change_color,
    config,
    crop,
    detect,
    draw_arrows,
    draw_circle,
    draw_lines,
    draw_rectangle,
    draw_text,
    fill,
    find,
    metainfo,
    ocr,
    overlay,
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
    log_level="DEBUG"
)

validation_middleware = ImprovedValidationMiddleware(logger=logger)
mcp.add_middleware(validation_middleware)

telemetry_middleware = TelemetryMiddleware(logger=logger)
mcp.add_middleware(telemetry_middleware)

error_middleware = ErrorHandlingMiddleware(
    logger=logger,
    include_traceback=True,
    transform_errors=True,
)
mcp.add_middleware(error_middleware)

# Register tools with the module-level mcp instance
blur.register_tool(mcp)
change_color.register_tool(mcp)
config.register_tool(mcp)
crop.register_tool(mcp)
detect.register_tool(mcp)
draw_arrows.register_tool(mcp)
draw_circle.register_tool(mcp)
draw_lines.register_tool(mcp)
draw_rectangle.register_tool(mcp)
draw_text.register_tool(mcp)
fill.register_tool(mcp)
find.register_tool(mcp)
metainfo.register_tool(mcp)
ocr.register_tool(mcp)
overlay.register_tool(mcp)
resize.register_tool(mcp)
rotate.register_tool(mcp)

# Register resources
models.register_resource(mcp)

# Register prompts
remove_background.register_prompt(mcp)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ImageSorcery MCP Server")
    parser.add_argument(
        "--post-install", 
        action="store_true", 
        help="Run post-installation tasks and exit"
    )
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "streamable-http", "sse"],
        help="Transport protocol to use (default: stdio)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to when using HTTP-based transports (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to when using HTTP-based transports (default: 8000)"
    )
    parser.add_argument(
        "--path",
        type=str,
        default="/mcp",
        help="Path for the MCP endpoint when using HTTP-based transports (default: /mcp)"
    )
    return parser.parse_args()

def main():
    """Main entry point for the server."""
    args = parse_arguments()
    
    logger.info("Starting 🪄 ImageSorcery MCP server setup")
    
    # Get version from package metadata
    try:
        from importlib.metadata import version
        package_version = version("imagesorcery-mcp")
        print(f"ImageSorcery MCP Version: {package_version}")
    except Exception as e:
        logger.error(f"Could not read version from package metadata: {e}")
        print("ImageSorcery MCP Version: unknown")

    
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
    logger.info(f"Starting MCP server with transport: {args.transport}")
    
    # Configure transport with appropriate parameters
    if args.transport in ["streamable-http", "sse"]:
        mcp.run(
            transport=args.transport,
            host=args.host,
            port=args.port,
            path=args.path
        )
    else:
        # Use default stdio transport
        mcp.run()

if __name__ == "__main__":
    main()
