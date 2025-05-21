import os
from typing import Annotated, Any, Dict, List, Optional

import cv2
from fastmcp import FastMCP
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def blur(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
        areas: Annotated[
            List[Dict[str, Any]],
            Field(
                description=(
                    "List of areas to blur. Each area should have: "
                    "'x1' (int), 'y1' (int), 'x2' (int), 'y2' (int) - coordinates of the bounding box, "
                    "and optionally 'blur_strength' (int) - the blur kernel size (odd number, default is 15)"
                )
            ),
        ],
        output_path: Annotated[
            Optional[str],
            Field(
                description=(
                    "Full path to save the output image (must be a full path). "
                    "If not provided, will use input filename "
                    "with '_blurred' suffix."
                )
            ),
        ] = None,
    ) -> str:
        """
        Blur specified areas of an image using OpenCV.
        
        This tool allows blurring multiple rectangular areas of an image with customizable
        blur strength. Each area is defined by a bounding box with coordinates [x1, y1, x2, y2]
        where (x1, y1) is the top-left corner and (x2, y2) is the bottom-right corner.
        
        The blur_strength parameter controls the intensity of the blur effect. Higher values
        result in stronger blur. It must be an odd number (default is 15).
        
        Returns:
            Path to the image with blurred areas
        """
        logger.info(f"Blur tool requested for image: {input_path} with {len(areas)} areas")

        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_blurred{file_ext}"
            logger.info(f"Output path not provided, generated: {output_path}")

        # Read the image using OpenCV
        logger.info(f"Reading image: {input_path}")
        img = cv2.imread(input_path)
        if img is None:
            logger.error(f"Failed to read image: {input_path}")
            raise ValueError(f"Failed to read image: {input_path}")
        logger.info(f"Image read successfully. Shape: {img.shape}")

        # Process each area to blur
        for i, area in enumerate(areas):
            # Extract coordinates (required)
            x1 = area["x1"]
            y1 = area["y1"]
            x2 = area["x2"]
            y2 = area["y2"]
            
            # Extract optional parameters with defaults
            blur_strength = area.get("blur_strength", 15)
            
            # Ensure blur_strength is odd (required for Gaussian blur)
            if blur_strength % 2 == 0:
                blur_strength += 1
                logger.warning(f"Adjusted blur_strength to odd number: {blur_strength}")
            
            logger.debug(f"Blurring area {i+1}: ({x1}, {y1}) to ({x2}, {y2}) with strength={blur_strength}")

            # Extract the region to blur
            region = img[y1:y2, x1:x2]
            
            # Apply Gaussian blur to the region
            blurred_region = cv2.GaussianBlur(region, (blur_strength, blur_strength), 0)
            
            # Replace the original region with the blurred one
            img[y1:y2, x1:x2] = blurred_region
            
            logger.debug(f"Area {i+1} blurred")

        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            logger.info(f"Output directory does not exist, creating: {output_dir}")
            os.makedirs(output_dir)
            logger.info(f"Output directory created: {output_dir}")

        # Save the image with blurred areas
        logger.info(f"Saving blurred image to: {output_path}")
        cv2.imwrite(output_path, img)
        logger.info(f"Blurred image saved successfully to: {output_path}")

        return output_path