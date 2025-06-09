import os
from typing import Annotated, Literal, Optional

import cv2
import numpy as np
from fastmcp import FastMCP
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def change_color(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
        palette: Annotated[
            Literal["grayscale", "sepia"],
            Field(description="The color palette to apply. Currently supports 'grayscale' and 'sepia'."),
        ],
        output_path: Annotated[
            Optional[str],
            Field(
                description=(
                    "Full path to save the output image (must be a full path). "
                    "If not provided, will use input filename "
                    "with a suffix based on the palette (e.g., '_grayscale')."
                )
            ),
        ] = None,
    ) -> str:
        """
        Change the color palette of an image.
        
        This tool applies a predefined color transformation to an image.
        Currently supported palettes are 'grayscale' and 'sepia'.
        
        Returns:
            Path to the image with the new color palette.
        """
        logger.info(f"Change color tool requested for image: {input_path} with palette: {palette}")

        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_{palette}{file_ext}"
            logger.info(f"Output path not provided, generated: {output_path}")

        # Read the image using OpenCV
        img = cv2.imread(input_path)
        if img is None:
            logger.error(f"Failed to read image: {input_path}")
            raise ValueError(f"Failed to read image: {input_path}")

        # Apply the selected color palette
        if palette == "grayscale":
            logger.info("Applying grayscale palette")
            output_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif palette == "sepia":
            logger.info("Applying sepia palette")
            # Sepia transformation matrix
            sepia_kernel = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
            # Apply the transformation
            sepia_img = cv2.transform(img, sepia_kernel)
            # Clip values to be in the 0-255 range
            output_img = np.clip(sepia_img, 0, 255).astype(np.uint8)

        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save the image
        cv2.imwrite(output_path, output_img)
        logger.info(f"Transformed image saved successfully to: {output_path}")

        return output_path