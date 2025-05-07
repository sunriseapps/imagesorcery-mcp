import os
from typing import Annotated

import cv2
from fastmcp import FastMCP
from pydantic import Field


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def crop(
        input_path: Annotated[str, Field(description="Path to the input image")],
        y_start: Annotated[
            int,
            Field(description="Starting y-coordinate (row) for the crop region (top)"),
        ],
        y_end: Annotated[
            int,
            Field(description="Ending y-coordinate (row) for the crop region (bottom)"),
        ],
        x_start: Annotated[
            int,
            Field(
                description="Starting x-coordinate (column) for the crop region (left)"
            ),
        ],
        x_end: Annotated[
            int,
            Field(
                description="Ending x-coordinate (column) for the crop region (right)"
            ),
        ],
        output_path: Annotated[
            str,
            Field(
                description=(
                    "Path to save the output image. "
                    "If not provided, will use input filename "
                    "with '_cropped' suffix."
                )
            ),
        ] = None,
    ) -> str:
        """
        Crop an image using OpenCV's NumPy slicing approach.

        The function uses the NumPy slicing syntax common in OpenCV:
        - image[y_start:y_end, x_start:x_end] selects a rectangular region
        - y coordinates represent rows (vertical axis, top to bottom)
        - x coordinates represent columns (horizontal axis, left to right)

        Returns:
            Path to the cropped image
        """
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_cropped{file_ext}"

        # Read the image using OpenCV
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Failed to read image: {input_path}")

        # Crop the image using NumPy slicing
        cropped_img = img[y_start:y_end, x_start:x_end]

        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save the cropped image
        cv2.imwrite(output_path, cropped_img)

        return output_path
