import os
from typing import Annotated, Any, Dict, List, Optional

import cv2
from fastmcp import FastMCP
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def draw_lines(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
        lines: Annotated[
            List[Dict[str, Any]],
            Field(
                description=(
                    "List of line items to draw. Each item should have: "
                    "'x1' (int), 'y1' (int) - start point, "
                    "'x2' (int), 'y2' (int) - end point, and optionally "
                    "'color' (list of 3 ints [B,G,R]), "
                    "'thickness' (int)"
                )
            ),
        ],
        output_path: Annotated[
            Optional[str],
            Field(
                description=(
                    "Full path to save the output image (must be a full path). "
                    "If not provided, will use input filename "
                    "with '_with_lines' suffix."
                )
            ),
        ] = None,
    ) -> str:
        """
        Draw lines on an image using OpenCV.
        
        This tool allows adding multiple lines to an image with customizable
        start and end points, color, and thickness.
        
        Each line is defined by its start point (x1, y1) and end point (x2, y2).
        
        Returns:
            Path to the image with drawn lines
        """
        logger.info(f"Draw lines tool requested for image: {input_path} with {len(lines)} lines")

        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_with_lines{file_ext}"
            logger.info(f"Output path not provided, generated: {output_path}")

        # Read the image using OpenCV
        logger.info(f"Reading image: {input_path}")
        img = cv2.imread(input_path)
        if img is None:
            logger.error(f"Failed to read image: {input_path}")
            raise ValueError(f"Failed to read image: {input_path}")
        logger.info(f"Image read successfully. Shape: {img.shape}")

        # Draw each line on the image
        for i, line_item in enumerate(lines):
            x1, y1 = line_item["x1"], line_item["y1"]
            x2, y2 = line_item["x2"], line_item["y2"]
            
            color = line_item.get("color", [0, 0, 0])  # Default: black
            thickness = line_item.get("thickness", 1)
            
            logger.debug(f"Drawing line {i+1}: from ({x1},{y1}) to ({x2},{y2}), color={color}, thickness={thickness}")

            cv2.line(img, (x1, y1), (x2, y2), color, thickness)
            logger.debug(f"Line {i+1} drawn")

        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            logger.info(f"Output directory does not exist, creating: {output_dir}")
            os.makedirs(output_dir)
            logger.info(f"Output directory created: {output_dir}")

        cv2.imwrite(output_path, img)
        logger.info(f"Image with lines saved successfully to: {output_path}")

        return output_path
