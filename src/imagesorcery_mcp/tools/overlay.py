import os
from typing import Annotated, Optional

import cv2
import numpy as np
from fastmcp import FastMCP
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def overlay(
        base_image_path: Annotated[str, Field(description="Full path to the base image (must be a full path)")],
        overlay_image_path: Annotated[
            str, Field(description="Full path to the overlay image (must be a full path). This image can have transparency.")
        ],
        x: Annotated[int, Field(description="X-coordinate of the top-left corner of the overlay image on the base image.")],
        y: Annotated[int, Field(description="Y-coordinate of the top-left corner of the overlay image on the base image.")],
        output_path: Annotated[
            Optional[str],
            Field(
                description=(
                    "Full path to save the output image (must be a full path). "
                    "If not provided, will use the base image filename "
                    "with '_overlaid' suffix."
                )
            ),
        ] = None,
    ) -> str:
        """
        Overlays one image on top of another, handling transparency.

        This tool places an overlay image onto a base image at a specified (x, y)
        coordinate. If the overlay image has an alpha channel (e.g., a transparent PNG),
        it will be blended correctly with the base image. If the overlay extends
        beyond the boundaries of the base image, it will be cropped.

        Returns:
            Path to the resulting image.
        """
        logger.info(f"Overlay tool requested for base image: {base_image_path}, overlay image: {overlay_image_path}")

        # Check if input files exist
        if not os.path.exists(base_image_path):
            logger.error(f"Base image not found: {base_image_path}")
            raise FileNotFoundError(f"Base image not found: {base_image_path}. Please provide a full path to the file.")
        if not os.path.exists(overlay_image_path):
            logger.error(f"Overlay image not found: {overlay_image_path}")
            raise FileNotFoundError(f"Overlay image not found: {overlay_image_path}. Please provide a full path to the file.")

        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(base_image_path)
            output_path = f"{file_name}_overlaid{file_ext}"
            logger.info(f"Output path not provided, generated: {output_path}")

        # Read images
        base_img = cv2.imread(base_image_path)
        overlay_img = cv2.imread(overlay_image_path, cv2.IMREAD_UNCHANGED)

        if base_img is None:
            logger.error(f"Failed to read base image: {base_image_path}")
            raise ValueError(f"Failed to read base image: {base_image_path}")
        if overlay_img is None:
            logger.error(f"Failed to read overlay image: {overlay_image_path}")
            raise ValueError(f"Failed to read overlay image: {overlay_image_path}")

        # Get dimensions
        base_h, base_w, _ = base_img.shape
        overlay_h, overlay_w, _ = overlay_img.shape

        # Handle coordinates and potential cropping of the overlay
        x_start, y_start = x, y
        x_end, y_end = x + overlay_w, y + overlay_h
        overlay_x_start, overlay_y_start = 0, 0
        overlay_x_end, overlay_y_end = overlay_w, overlay_h

        if x_start < 0:
            overlay_x_start = -x_start
            x_start = 0
        if y_start < 0:
            overlay_y_start = -y_start
            y_start = 0
        if x_end > base_w:
            overlay_x_end -= x_end - base_w
            x_end = base_w
        if y_end > base_h:
            overlay_y_end -= y_end - base_h
            y_end = base_h

        if x_start >= x_end or y_start >= y_end:
            logger.warning("Overlay is completely outside the base image. No changes made.")
            cv2.imwrite(output_path, base_img)
            return output_path

        overlay_img = overlay_img[overlay_y_start:overlay_y_end, overlay_x_start:overlay_x_end]
        roi = base_img[y_start:y_end, x_start:x_end]

        if overlay_img.shape[2] == 4:
            logger.info("Overlay image has alpha channel. Performing alpha blending.")
            alpha = overlay_img[:, :, 3] / 255.0
            overlay_colors = overlay_img[:, :, :3]
            alpha_mask = cv2.merge([alpha, alpha, alpha])
            blended_roi = (alpha_mask * overlay_colors) + ((1 - alpha_mask) * roi)
            base_img[y_start:y_end, x_start:x_end] = blended_roi.astype(np.uint8)
        else:
            logger.info("Overlay image has no alpha channel. Pasting directly.")
            base_img[y_start:y_end, x_start:x_end] = overlay_img

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        cv2.imwrite(output_path, base_img)
        logger.info(f"Overlaid image saved successfully to: {output_path}")

        return output_path
