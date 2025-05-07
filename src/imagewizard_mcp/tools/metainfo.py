import datetime
import os
from typing import Annotated, Any, Dict

from fastmcp import FastMCP
from PIL import Image
from pydantic import Field


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def get_metainfo(
        input_path: Annotated[str, Field(description="Path to the input image")],
    ) -> Dict[str, Any]:
        """
        Get metadata information about an image file.

        Returns:
            Dictionary containing metadata about the image (size, dimensions,
            format, etc.)
        """
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Get file stats
        file_stats = os.stat(input_path)
        file_size = file_stats.st_size
        creation_time = datetime.datetime.fromtimestamp(file_stats.st_ctime)
        modification_time = datetime.datetime.fromtimestamp(file_stats.st_mtime)

        # Get image-specific information
        with Image.open(input_path) as img:
            width, height = img.size
            format = img.format
            mode = img.mode

            # Try to get additional info if available
            info = {}
            if hasattr(img, "info"):
                info = img.info

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
            "additional_info": info,
        }

        return metadata
