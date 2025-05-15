import os
from typing import Annotated

import cv2
import imutils
from fastmcp import FastMCP
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def rotate(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
        angle: Annotated[
            float,
            Field(
                description=(
                    "Angle of rotation in degrees (positive for counterclockwise)"
                )
            ),
        ],
        output_path: Annotated[
            str,
            Field(
                description=(
                    "Full path to save the output image (must be a full path). "
                    "If not provided, will use input filename "
                    "with '_rotated' suffix."
                )
            ),
        ] = None,
    ) -> str:
        """
        Rotate an image using imutils.rotate_bound function.

        The function rotates the image by the specified angle in degrees.
        Positive angles represent counterclockwise rotation.
        The rotate_bound function ensures the entire rotated image is visible
        by automatically adjusting the output image size.

        Returns:
            Path to the rotated image
        """
        logger.info(f"Rotate tool requested for image: {input_path} with angle: {angle} degrees")

        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")
        logger.info(f"Input file found: {input_path}")

        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_rotated{file_ext}"
            logger.info(f"Output path not provided, generated: {output_path}")

        # Read the image using OpenCV
        logger.info(f"Reading image: {input_path}")
        img = cv2.imread(input_path)
        if img is None:
            logger.error(f"Failed to read image: {input_path}")
            raise ValueError(f"Failed to read image: {input_path}")
        logger.info(f"Image read successfully. Shape: {img.shape}")

        # Rotate the image using imutils.rotate_bound
        logger.info(f"Rotating image by {angle} degrees")
        rotated_img = imutils.rotate_bound(img, angle)
        logger.info(f"Image rotated successfully. New shape: {rotated_img.shape}")

        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            logger.info(f"Output directory does not exist, creating: {output_dir}")
            os.makedirs(output_dir)
            logger.info(f"Output directory created: {output_dir}")

        # Save the rotated image
        logger.info(f"Saving rotated image to: {output_path}")
        cv2.imwrite(output_path, rotated_img)
        logger.info(f"Rotated image saved successfully to: {output_path}")

        return output_path
