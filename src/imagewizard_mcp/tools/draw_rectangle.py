import os
from typing import Annotated, Any, Dict, List, Optional

import cv2
from fastmcp import FastMCP
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def draw_rectangles(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
        rectangles: Annotated[
            List[Dict[str, Any]],
            Field(
                description=(
                    "List of rectangle items to draw. Each item should have: "
                    "'x1' (int), 'y1' (int), 'x2' (int), 'y2' (int), and optionally "
                    "'color' (list of 3 ints [B,G,R]), "
                    "'thickness' (int), 'filled' (bool)"
                )
            ),
        ],
        output_path: Annotated[
            Optional[str],
            Field(
                description=(
                    "Full path to save the output image (must be a full path). "
                    "If not provided, will use input filename "
                    "with '_with_rectangles' suffix."
                )
            ),
        ] = None,
    ) -> str:
        """
        Draw rectangles on an image using OpenCV.
        
        This tool allows adding multiple rectangles to an image with customizable
        position, color, thickness, and fill option.
        
        Each rectangle is defined by two points: (x1, y1) for the top-left corner
        and (x2, y2) for the bottom-right corner.
        
        Returns:
            Path to the image with drawn rectangles
        """
        logger.info(f"Draw rectangles tool requested for image: {input_path} with {len(rectangles)} rectangles")

        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_with_rectangles{file_ext}"
            logger.info(f"Output path not provided, generated: {output_path}")

        # Read the image using OpenCV
        logger.info(f"Reading image: {input_path}")
        img = cv2.imread(input_path)
        if img is None:
            logger.error(f"Failed to read image: {input_path}")
            raise ValueError(f"Failed to read image: {input_path}")
        logger.info(f"Image read successfully. Shape: {img.shape}")

        # Draw each rectangle on the image
        for i, rect_item in enumerate(rectangles):
            # Extract rectangle coordinates (required)
            x1 = rect_item["x1"]
            y1 = rect_item["y1"]
            x2 = rect_item["x2"]
            y2 = rect_item["y2"]
            
            # Extract optional parameters with defaults
            color = rect_item.get("color", [0, 0, 0])  # Default: black
            thickness = rect_item.get("thickness", 1)
            filled = rect_item.get("filled", False)
            
            logger.debug(f"Drawing rectangle {i+1}: x1={x1}, y1={y1}, x2={x2}, y2={y2}, color={color}, thickness={thickness}, filled={filled}")

            # If filled is True, set thickness to -1 (OpenCV's way of filling shapes)
            if filled:
                thickness = -1
            
            # Draw the rectangle on the image
            cv2.rectangle(
                img, 
                (x1, y1), 
                (x2, y2), 
                color, 
                thickness
            )
            logger.debug(f"Rectangle {i+1} drawn")

        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            logger.info(f"Output directory does not exist, creating: {output_dir}")
            os.makedirs(output_dir)
            logger.info(f"Output directory created: {output_dir}")

        # Save the image with rectangles
        logger.info(f"Saving image with rectangles to: {output_path}")
        cv2.imwrite(output_path, img)
        logger.info(f"Image with rectangles saved successfully to: {output_path}")

        return output_path
