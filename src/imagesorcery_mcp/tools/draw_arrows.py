import os
from typing import Annotated, Any, Dict, List, Optional

import cv2
from fastmcp import FastMCP
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def draw_arrows(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
        arrows: Annotated[
            List[Dict[str, Any]],
            Field(
                description=(
                    "List of arrow items to draw. Each item should have: "
                    "'x1' (int), 'y1' (int) - start point, "
                    "'x2' (int), 'y2' (int) - end point, and optionally "
                    "'color' (list of 3 ints [B,G,R]), "
                    "'thickness' (int), 'tip_length' (float, relative to arrow length)"
                )
            ),
        ],
        output_path: Annotated[
            Optional[str],
            Field(
                description=(
                    "Full path to save the output image (must be a full path). "
                    "If not provided, will use input filename "
                    "with '_with_arrows' suffix."
                )
            ),
        ] = None,
    ) -> str:
        """
        Draw arrows on an image using OpenCV.
        
        This tool allows adding multiple arrows to an image with customizable
        start and end points, color, thickness, and tip length.
        
        Each arrow is defined by its start point (x1, y1) and end point (x2, y2).
        The 'tip_length' is relative to the arrow's length (e.g., 0.1 means 10%).
        
        Returns:
            Path to the image with drawn arrows
        """
        logger.info(f"Draw arrows tool requested for image: {input_path} with {len(arrows)} arrows")

        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_with_arrows{file_ext}"
            logger.info(f"Output path not provided, generated: {output_path}")

        # Read the image using OpenCV
        logger.info(f"Reading image: {input_path}")
        img = cv2.imread(input_path)
        if img is None:
            logger.error(f"Failed to read image: {input_path}")
            raise ValueError(f"Failed to read image: {input_path}")
        logger.info(f"Image read successfully. Shape: {img.shape}")

        # Draw each arrow on the image
        for i, arrow_item in enumerate(arrows):
            x1, y1 = arrow_item["x1"], arrow_item["y1"]
            x2, y2 = arrow_item["x2"], arrow_item["y2"]
            
            color = arrow_item.get("color", [0, 0, 0])  # Default: black
            thickness = arrow_item.get("thickness", 1)
            tip_length = arrow_item.get("tip_length", 0.1)
            
            logger.debug(f"Drawing arrow {i+1}: from ({x1},{y1}) to ({x2},{y2}), color={color}, thickness={thickness}, tip_length={tip_length}")

            cv2.arrowedLine(img, (x1, y1), (x2, y2), color, thickness, tipLength=tip_length)
            logger.debug(f"Arrow {i+1} drawn")

        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            logger.info(f"Output directory does not exist, creating: {output_dir}")
            os.makedirs(output_dir)
            logger.info(f"Output directory created: {output_dir}")

        cv2.imwrite(output_path, img)
        logger.info(f"Image with arrows saved successfully to: {output_path}")

        return output_path
