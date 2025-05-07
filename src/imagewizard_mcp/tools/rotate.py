import os
from typing import Annotated

import cv2
import imutils
from fastmcp import FastMCP
from pydantic import Field


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def rotate(
        input_path: Annotated[str, Field(description="Path to the input image")],
        angle: Annotated[float, Field(description="Angle of rotation in degrees (positive for counterclockwise)")],
        output_path: Annotated[str, Field(description="Path to save the output image. If not provided, will use input filename with '_rotated' suffix.")] = None
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
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_rotated{file_ext}"
        
        # Read the image using OpenCV
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Failed to read image: {input_path}")
            
        # Rotate the image using imutils.rotate_bound
        rotated_img = imutils.rotate_bound(img, angle)
        
        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Save the rotated image
        cv2.imwrite(output_path, rotated_img)
            
        return output_path