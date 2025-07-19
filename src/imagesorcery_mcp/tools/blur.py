import os
from typing import Annotated, Any, Dict, List, Optional

import cv2
import numpy as np
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
                    "a rectangle ({'x1', 'y1', 'x2', 'y2'}) or a polygon ({'polygon': [[x,y],...]}). "
                    "Optionally, include 'blur_strength' (int, odd number, default 15) for each area."
                )
            ),
        ],
        invert_areas: Annotated[
            bool,
            Field(
                description="If True, blurs everything EXCEPT the specified areas. Useful for background blurring."
            ),
        ] = False,
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
        Blur specified rectangular or polygonal areas of an image using OpenCV.
        
        This tool allows blurring multiple rectangular or polygonal areas of an image with customizable
        blur strength. Each area can be a rectangle defined by a bounding box 
        [x1, y1, x2, y2] or a polygon defined by a list of points.
        
        The blur_strength parameter controls the intensity of the blur effect. Higher values
        result in stronger blur. It must be an odd number (default is 15).
        
        If `invert_areas` is True, the tool will blur everything EXCEPT the specified areas.
        Returns:
            Path to the image with blurred areas
        """
        logger.info(f"Blur tool requested for image: {input_path} with {len(areas)} areas, invert_areas={invert_areas}")

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

        # Create a mask for the areas to be blurred (or not blurred if invert_areas is True)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)

        # Populate the mask based on areas
        for area in areas:
            if "polygon" in area:
                polygon_points = np.array(area["polygon"], dtype=np.int32)
                cv2.fillPoly(mask, [polygon_points], 255)
            elif "x1" in area and "y1" in area and "x2" in area and "y2" in area:
                x1, y1, x2, y2 = area["x1"], area["y1"], area["x2"], area["y2"]
                cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
            else:
                logger.warning("Skipping area due to missing 'polygon' or 'x1,y1,x2,y2' keys.")
                continue

        # If invert_areas is True, invert the mask
        if invert_areas:
            mask = cv2.bitwise_not(mask)
            logger.info("Inverting blur areas: blurring everything EXCEPT the specified regions.")
        else:
            logger.info("Applying blur to specified areas.")

        # Apply blur to the entire image (this will be used for the masked regions)
        # Use the blur_strength from the first area, or default to 15
        global_blur_strength = areas[0].get("blur_strength", 15) if areas else 15
        if global_blur_strength % 2 == 0:
            global_blur_strength += 1
            logger.warning(f"Adjusted global blur_strength to odd number: {global_blur_strength}")
        
        full_blurred_img = cv2.GaussianBlur(img, (global_blur_strength, global_blur_strength), 0)

        # Combine the original image and the fully blurred image using the mask
        # Where mask is 255 (white), use the blurred image. Where mask is 0 (black), use the original image.
        result_img = np.where(mask[:, :, None] == 255, full_blurred_img, img)

        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            logger.info(f"Output directory does not exist, creating: {output_dir}")
            os.makedirs(output_dir)
            logger.info(f"Output directory created: {output_dir}")

        # Save the image with blurred areas
        logger.info(f"Saving blurred image to: {output_path}")
        cv2.imwrite(output_path, result_img)
        logger.info(f"Blurred image saved successfully to: {output_path}")

        return output_path
