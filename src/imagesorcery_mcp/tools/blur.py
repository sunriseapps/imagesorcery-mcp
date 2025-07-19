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
        
        This tool allows blurring multiple rectangular areas of an image with customizable
        blur strength. Each area can be a rectangle defined by a bounding box 
        [x1, y1, x2, y2] or a polygon defined by a list of points.
        
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
            # Extract optional parameters with defaults
            blur_strength = area.get("blur_strength", 15)

            # Ensure blur_strength is odd (required for Gaussian blur)
            if blur_strength % 2 == 0:
                blur_strength += 1
                logger.warning(f"Adjusted blur_strength to odd number: {blur_strength}")

            if "polygon" in area:
                # It's a polygon
                logger.debug(f"Blurring polygon area {i+1} with strength={blur_strength}")
                polygon_points = np.array(area["polygon"], dtype=np.int32)

                # Create a mask for the polygon
                mask = np.zeros(img.shape[:2], dtype=np.uint8)
                cv2.fillPoly(mask, [polygon_points], (255))

                # Get the bounding box of the polygon to process only that region for efficiency
                x, y, w, h = cv2.boundingRect(polygon_points)

                # Extract the region of interest (ROI) from the original image
                roi = img[y : y + h, x : x + w]

                # Blur the ROI
                blurred_roi = cv2.GaussianBlur(roi, (blur_strength, blur_strength), 0)

                # Get the mask for the ROI
                roi_mask = mask[y : y + h, x : x + w]

                # Use the mask to combine the blurred ROI and original ROI
                roi_mask_inv = cv2.bitwise_not(roi_mask)
                img_bg = cv2.bitwise_and(roi, roi, mask=roi_mask_inv)
                img_fg = cv2.bitwise_and(blurred_roi, blurred_roi, mask=roi_mask)
                combined_roi = cv2.add(img_bg, img_fg)

                # Place the combined ROI back into the image
                img[y : y + h, x : x + w] = combined_roi
                logger.debug(f"Polygon area {i+1} blurred")

            elif "x1" in area and "y1" in area and "x2" in area and "y2" in area:
                # It's a rectangle (existing logic)
                x1, y1, x2, y2 = area["x1"], area["y1"], area["x2"], area["y2"]
                logger.debug(f"Blurring rectangle area {i+1}: ({x1}, {y1}) to ({x2}, {y2}) with strength={blur_strength}")
                region = img[y1:y2, x1:x2]
                blurred_region = cv2.GaussianBlur(region, (blur_strength, blur_strength), 0)
                img[y1:y2, x1:x2] = blurred_region
                logger.debug(f"Rectangle area {i+1} blurred")
            else:
                logger.warning(f"Skipping area {i+1} due to missing 'polygon' or 'x1,y1,x2,y2' keys.")
                continue

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
