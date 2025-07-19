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
    def fill(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
        areas: Annotated[
            List[Dict[str, Any]],
            Field(
                description=(
                    "List of areas to fill. Each area should have: "
                    "a rectangle ({'x1', 'y1', 'x2', 'y2'}) or a polygon ({'polygon': [[x,y],...]}). "
                    "Optionally, include 'color' (list of 3 ints [B,G,R], default [0,0,0]) and "
                    "'opacity' (float 0.0-1.0, default 0.5) for each area."
                )
            ),
        ],
        output_path: Annotated[
            Optional[str],
            Field(
                description=(
                    "Full path to save the output image (must be a full path). "
                    "If not provided, will use input filename "
                    "with '_filled' suffix."
                )
            ),
        ] = None,
    ) -> str:
        """
        Fill specified rectangular or polygonal areas of an image with a color and opacity.
        
        This tool allows filling multiple areas of an image with a customizable
        color and opacity. Each area can be a rectangle defined by a bounding box 
        [x1, y1, x2, y2] or a polygon defined by a list of points.
        
        The 'opacity' parameter controls the transparency of the fill. 1.0 is fully opaque,
        0.0 is fully transparent. Default is 0.5.
        The 'color' is in BGR format, e.g., [255, 0, 0] for blue. Default is black [0,0,0].
        
        Returns:
            Path to the image with filled areas
        """
        logger.info(f"Fill tool requested for image: {input_path} with {len(areas)} areas")

        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_filled{file_ext}"
            logger.info(f"Output path not provided, generated: {output_path}")

        # Read the image using OpenCV
        logger.info(f"Reading image: {input_path}")
        img = cv2.imread(input_path)
        if img is None:
            logger.error(f"Failed to read image: {input_path}")
            raise ValueError(f"Failed to read image: {input_path}")
        logger.info(f"Image read successfully. Shape: {img.shape}")

        # Process each area to fill
        for i, area in enumerate(areas):
            # Extract optional parameters with defaults
            color = tuple(area.get("color", [0, 0, 0]))
            opacity = area.get("opacity", 0.5)

            if not (0.0 <= opacity <= 1.0):
                logger.warning(f"Opacity {opacity} is outside the valid range [0.0, 1.0]. Clamping it.")
                opacity = max(0.0, min(1.0, opacity))

            if "polygon" in area:
                # It's a polygon
                logger.debug(f"Filling polygon area {i+1} with color={color}, opacity={opacity}")
                polygon_points = np.array(area["polygon"], dtype=np.int32)

                # Create a mask for the polygon
                mask = np.zeros(img.shape[:2], dtype=np.uint8)
                cv2.fillPoly(mask, [polygon_points], (255))

                # Get the bounding box of the polygon to process only that region for efficiency
                x, y, w, h = cv2.boundingRect(polygon_points)
                
                # Extract the region of interest (ROI) from the original image
                roi = img[y : y + h, x : x + w]

                # Create a solid color image for the ROI
                color_roi = np.full(roi.shape, color, dtype=np.uint8)

                # Blend the color and original ROI
                blended_roi = cv2.addWeighted(color_roi, opacity, roi, 1 - opacity, 0)

                # Get the mask for the ROI
                roi_mask = mask[y : y + h, x : x + w]

                # Use the mask to combine the blended ROI and original ROI
                img[y : y + h, x : x + w] = np.where(roi_mask[:, :, None] == 255, blended_roi, roi)
                logger.debug(f"Polygon area {i+1} filled")

            elif "x1" in area and "y1" in area and "x2" in area and "y2" in area:
                # It's a rectangle
                x1, y1, x2, y2 = area["x1"], area["y1"], area["x2"], area["y2"]
                logger.debug(f"Filling rectangle area {i+1}: ({x1}, {y1}) to ({x2}, {y2}) with color={color}, opacity={opacity}")
                
                roi = img[y1:y2, x1:x2]
                color_rect = np.full(roi.shape, color, dtype=np.uint8)
                blended_roi = cv2.addWeighted(color_rect, opacity, roi, 1 - opacity, 0)
                img[y1:y2, x1:x2] = blended_roi
                logger.debug(f"Rectangle area {i+1} filled")
            else:
                logger.warning(f"Skipping area {i+1} due to missing 'polygon' or 'x1,y1,x2,y2' keys.")
                continue

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        logger.info(f"Saving filled image to: {output_path}")
        cv2.imwrite(output_path, img)
        logger.info(f"Filled image saved successfully to: {output_path}")

        return output_path
