import os
from typing import Annotated

import cv2
from fastmcp import FastMCP
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def crop(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
        x1: Annotated[
            int,
            Field(description="X-coordinate of the top-left corner"),
        ],
        y1: Annotated[
            int,
            Field(description="Y-coordinate of the top-left corner"),
        ],
        x2: Annotated[
            int,
            Field(description="X-coordinate of the bottom-right corner"),
        ],
        y2: Annotated[
            int,
            Field(description="Y-coordinate of the bottom-right corner"),
        ],
        output_path: Annotated[
            str,
            Field(
                description=(
                    "Full path to save the output image (must be a full path). "
                    "If not provided, will use input filename "
                    "with '_cropped' suffix."
                )
            ),
        ] = None,
    ) -> str:
        """
        Crop an image using OpenCV's NumPy slicing approach
        with OpenMCP's bounding box annotations.

        Returns:
            Path to the cropped image
        """
        logger.info(f"Crop tool requested for image: {input_path} with region [{x1}, {y1}, {x2}, {y2}]")

        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_cropped{file_ext}"
            logger.info(f"Output path not provided, generated: {output_path}")

        # Read the image using OpenCV
        logger.info(f"Reading image: {input_path}")
        img = cv2.imread(input_path)
        if img is None:
            logger.error(f"Failed to read image: {input_path}")
            raise ValueError(f"Failed to read image: {input_path}")
        logger.info(f"Image read successfully. Shape: {img.shape}")

        # Crop the image using NumPy slicing
        logger.info(f"Cropping image with region [{x1}, {y1}, {x2}, {y2}]")
        cropped_img = img[y1:y2, x1:x2]
        logger.info(f"Image cropped successfully. New shape: {cropped_img.shape}")

        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            logger.info(f"Output directory does not exist, creating: {output_dir}")
            os.makedirs(output_dir)
            logger.info(f"Output directory created: {output_dir}")

        # Save the cropped image
        logger.info(f"Saving cropped image to: {output_path}")
        cv2.imwrite(output_path, cropped_img)
        logger.info(f"Cropped image saved successfully to: {output_path}")

        return output_path
