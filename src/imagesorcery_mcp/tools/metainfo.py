import datetime
import os
from typing import Annotated, Any

from fastmcp import FastMCP
from PIL import Image
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def get_metainfo(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
    ) -> Any:
        """
        Get metadata information about an image file.

        Returns:
            Dictionary containing metadata about the image (size, dimensions,
            format, etc.)
        """
        logger.info(f"Get metainfo tool requested for image: {input_path}")

        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")
        logger.info(f"Input file found: {input_path}")

        # Get file stats
        logger.info(f"Getting file stats for: {input_path}")
        file_stats = os.stat(input_path)
        file_size = file_stats.st_size
        creation_time = datetime.datetime.fromtimestamp(file_stats.st_ctime)
        modification_time = datetime.datetime.fromtimestamp(file_stats.st_mtime)
        logger.info(f"File size: {file_size} bytes, Created: {creation_time}, Modified: {modification_time}")

        # Get image-specific information
        logger.info(f"Opening image with PIL: {input_path}")
        try:
            with Image.open(input_path) as img:
                width, height = img.size
                format = img.format
                mode = img.mode

                logger.info(f"Image opened successfully. Dimensions: {width}x{height}, Format: {format}, Mode: {mode}")
        except Exception as e:
            logger.error(f"Failed to open image with PIL: {input_path} - {str(e)}")
            raise ValueError(f"Failed to read image: {input_path}") from e


        # Compile all metadata
        metadata = {
            "filename": os.path.basename(input_path),
            "path": input_path,
            "size_bytes": file_size,
            "size_kb": round(file_size / 1024, 2),
            "size_mb": round(file_size / (1024 * 1024), 2),
            "dimensions": {
                "width": width,
                "height": height,
                "aspect_ratio": round(width / height, 2) if height != 0 else None,
            },
            "format": format,
            "color_mode": mode,
            "created_at": creation_time.isoformat(),
            "modified_at": modification_time.isoformat(),
        }
        logger.info("Metadata compiled successfully")
        logger.debug(f"Metadata: {metadata}")

        return metadata
