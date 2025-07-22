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
                    "Optionally, include 'color' (list of 3 ints [B,G,R] or None, default black) and "
                    "'opacity' (float 0.0-1.0, default 0.5) INSIDE each area object. "
                    "Example: [{'polygon': [[0,0], [100,0], [100,100]], 'color': [255,0,0], 'opacity': 0.5}]"
                )
            ),
        ],
        invert_areas: Annotated[
            bool,
            Field(
                description="If True, fills everything EXCEPT the specified areas. Useful for background removal."
            ),
        ] = False,
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
        The 'color' is in BGR format, e.g., [255, 0, 0] for blue. Default is black.

        If the `color` is set to `None`, the specified area will be made fully transparent,
        effectively deleting it (similar to ImageMagick). In this case, the `opacity`
        parameter is ignored.
        
        If `invert_areas` is True, the tool will fill everything EXCEPT the specified areas.

        Example usage:
        {
            "input_path": "/path/to/image.jpg",
            "areas": [
                {
                    "polygon": [[0, 0], [100, 0], [100, 100], [0, 100]],
                    "color": null,  // Makes area transparent
                    "opacity": 1.0
                }
            ],
            "invert_areas": true,  // Removes background, keeps only the polygon area
            "output_path": "/path/to/output.png"
        }
        
        Returns:
            Path to the image with filled areas
        """
        logger.info(f"Fill tool requested for image: {input_path} with {len(areas)} areas, invert_areas={invert_areas}")

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
        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            logger.error(f"Failed to read image: {input_path}")
            raise ValueError(f"Failed to read image: {input_path}")
        logger.info(f"Image read successfully. Shape: {img.shape}")

        # If any area requests transparency OR invert_areas is used with transparency, ensure we have an alpha channel
        if any(area.get("color") is None for area in areas) or (invert_areas and areas and areas[0].get("color") is None):
            if len(img.shape) < 3 or img.shape[2] == 3:
                logger.info("Converting image to BGRA to support transparency")
                img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA if len(img.shape) > 2 and img.shape[2] == 3 else cv2.COLOR_GRAY2BGRA)

        # Create mask for invert mode if needed
        if invert_areas:
            # Create a mask where specified areas are 0 (don't fill) and everything else is 255 (fill)
            mask = np.ones(img.shape[:2], dtype=np.uint8) * 255
            
            # Mark each area as 0 (don't fill)
            for area in areas:
                if "polygon" in area:
                    polygon_points = np.array(area["polygon"], dtype=np.int32)
                    cv2.fillPoly(mask, [polygon_points], 0)
                elif "x1" in area and "y1" in area and "x2" in area and "y2" in area:
                    x1, y1, x2, y2 = area["x1"], area["y1"], area["x2"], area["y2"]
                    mask[y1:y2, x1:x2] = 0
            
            # Get fill parameters from the first area
            color = areas[0].get("color") if areas else None
            opacity = areas[0].get("opacity", 0.5) if areas else 0.5
            
            logger.info("Inverted areas: applying fill to masked regions")
            
            # Apply the fill using the mask
            if color is None:
                # Make masked areas transparent
                if img.shape[2] != 4:
                    raise ValueError("Image must have an alpha channel for transparency operations.")
                # Set alpha to 0 where mask is 255
                img[:, :, 3] = np.where(mask == 255, 0, img[:, :, 3])
            else:
                # Fill with color where mask is 255
                color_tuple = tuple(color)
                if not (0.0 <= opacity <= 1.0):
                    logger.warning(f"Opacity {opacity} is outside the valid range [0.0, 1.0]. Clamping it.")
                    opacity = max(0.0, min(1.0, opacity))
                
                # Create an overlay image
                overlay = img.copy()
                overlay[mask == 255] = color_tuple + (255,) if img.shape[2] == 4 else color_tuple
                
                # Blend the overlay with the original image
                img = np.where(mask[:, :, None] == 255, 
                              cv2.addWeighted(overlay, opacity, img, 1 - opacity, 0),
                              img)
        else:
            # Normal mode - process each area to fill
            for i, area in enumerate(areas):
                color = area.get("color")

                if color is None:
                    # Make area transparent
                    logger.debug(f"Making area {i+1} transparent")
                    if img.shape[2] != 4:
                        raise ValueError("Image must have an alpha channel for transparency operations.")
                    
                    transparent_color = (0, 0, 0, 0)
                    if "polygon" in area:
                        polygon_points = np.array(area["polygon"], dtype=np.int32)
                        cv2.fillPoly(img, [polygon_points], transparent_color)
                        logger.debug(f"Polygon area {i+1} made transparent")
                    elif "x1" in area and "y1" in area and "x2" in area and "y2" in area:
                        x1, y1, x2, y2 = area["x1"], area["y1"], area["x2"], area["y2"]
                        img[y1:y2, x1:x2] = transparent_color
                        logger.debug(f"Rectangle area {i+1} made transparent")
                    else:
                        logger.warning(f"Skipping area {i+1} due to missing 'polygon' or 'x1,y1,x2,y2' keys.")
                else:
                    # Fill with color
                    color_tuple = tuple(color)
                    opacity = area.get("opacity", 0.5)

                    if not (0.0 <= opacity <= 1.0):
                        logger.warning(f"Opacity {opacity} is outside the valid range [0.0, 1.0]. Clamping it.")
                        opacity = max(0.0, min(1.0, opacity))

                    if "polygon" in area:
                        logger.debug(f"Filling polygon area {i+1} with color={color_tuple}, opacity={opacity}")
                        polygon_points = np.array(area["polygon"], dtype=np.int32)
                        mask = np.zeros(img.shape[:2], dtype=np.uint8)
                        cv2.fillPoly(mask, [polygon_points], (255))
                        x, y, w, h = cv2.boundingRect(polygon_points)
                        roi = img[y : y + h, x : x + w]
                        
                        overlay_roi = roi.copy()
                        cv2.fillPoly(overlay_roi, [polygon_points - [x, y]], color_tuple)
                        blended_roi = cv2.addWeighted(overlay_roi, opacity, roi, 1 - opacity, 0)
                        
                        roi_mask = mask[y : y + h, x : x + w]
                        img[y : y + h, x : x + w] = np.where(roi_mask[:, :, None] == 255, blended_roi, roi)
                        logger.debug(f"Polygon area {i+1} filled")

                    elif "x1" in area and "y1" in area and "x2" in area and "y2" in area:
                        x1, y1, x2, y2 = area["x1"], area["y1"], area["x2"], area["y2"]
                        logger.debug(f"Filling rectangle area {i+1}: ({x1}, {y1}) to ({x2}, {y2}) with color={color_tuple}, opacity={opacity}")
                        
                        roi = img[y1:y2, x1:x2]
                        overlay_roi = roi.copy()
                        cv2.rectangle(overlay_roi, (0, 0), (roi.shape[1], roi.shape[0]), color_tuple, -1)
                        blended_roi = cv2.addWeighted(overlay_roi, opacity, roi, 1 - opacity, 0)
                        img[y1:y2, x1:x2] = blended_roi
                        logger.debug(f"Rectangle area {i+1} filled")
                    else:
                        logger.warning(f"Skipping area {i+1} due to missing 'polygon' or 'x1,y1,x2,y2' keys.")

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        logger.info(f"Saving filled image to: {output_path}")
        cv2.imwrite(output_path, img)
        logger.info(f"Filled image saved successfully to: {output_path}")

        return output_path
