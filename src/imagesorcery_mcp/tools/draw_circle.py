import os
from typing import Annotated, List, Optional

import cv2
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


class CircleItem(BaseModel):
    """Represents a circle to be drawn on an image."""
    center_x: Annotated[int, Field(description="X-coordinate of the circle's center")]
    center_y: Annotated[int, Field(description="Y-coordinate of the circle's center")]
    radius: Annotated[int, Field(description="Radius of the circle")]
    color: Annotated[Optional[List[int]], Field(description="Color in BGR format [B,G,R]")] = [0, 0, 0]  # Default: black
    thickness: Annotated[Optional[int], Field(description="Line thickness. Use -1 for a filled circle.")] = 1
    filled: Annotated[Optional[bool], Field(description="Whether to fill the circle. If true, thickness is set to -1.")] = False


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def draw_circles(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
        circles: Annotated[
            List[CircleItem],
            Field(
                description=(
                    "List of circle items to draw. Each item should have: "
                    "'center_x' (int), 'center_y' (int), 'radius' (int), and optionally "
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
                    "with '_with_circles' suffix."
                )
            ),
        ] = None,
    ) -> str:
        """
        Draw circles on an image using OpenCV.
        
        This tool allows adding multiple circles to an image with customizable
        center, radius, color, thickness, and fill option.
        
        Each circle is defined by its center coordinates (center_x, center_y) and radius.
        
        Returns:
            Path to the image with drawn circles
        """
        logger.info(f"Draw circles tool requested for image: {input_path} with {len(circles)} circles")

        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_with_circles{file_ext}"
            logger.info(f"Output path not provided, generated: {output_path}")

        # Read the image using OpenCV
        logger.info(f"Reading image: {input_path}")
        img = cv2.imread(input_path)
        if img is None:
            logger.error(f"Failed to read image: {input_path}")
            raise ValueError(f"Failed to read image: {input_path}")
        logger.info(f"Image read successfully. Shape: {img.shape}")

        # Draw each circle on the image
        for i, circle_item in enumerate(circles):
            center_x = circle_item.center_x
            center_y = circle_item.center_y
            radius = circle_item.radius
            color = circle_item.color
            thickness = circle_item.thickness
            filled = circle_item.filled
            
            logger.debug(f"Drawing circle {i+1}: center=({center_x}, {center_y}), radius={radius}, color={color}, thickness={thickness}, filled={filled}")

            if filled:
                thickness = -1
            
            cv2.circle(img, (center_x, center_y), radius, color, thickness)
            logger.debug(f"Circle {i+1} drawn")

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Output directory created: {output_dir}")

        cv2.imwrite(output_path, img)
        logger.info(f"Image with circles saved successfully to: {output_path}")

        return output_path
