import os
from typing import Annotated, Optional

import cv2
from fastmcp import FastMCP
from pydantic import Field


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def resize(
        input_path: Annotated[str, Field(description="Path to the input image")],
        width: Annotated[Optional[int], Field(description="Target width in pixels. If None, will be calculated based on height and preserve aspect ratio")] = None,
        height: Annotated[Optional[int], Field(description="Target height in pixels. If None, will be calculated based on width and preserve aspect ratio")] = None,
        scale_factor: Annotated[Optional[float], Field(description="Scale factor to resize the image (e.g., 0.5 for half size, 2.0 for double size). Overrides width and height if provided")] = None,
        interpolation: Annotated[str, Field(description="Interpolation method: 'nearest', 'linear', 'area', 'cubic', 'lanczos'")] = "linear",
        output_path: Annotated[str, Field(description="Path to save the output image. If not provided, will use input filename with '_resized' suffix.")] = None
    ) -> str:
        """
        Resize an image using OpenCV.
        
        The function can resize an image in three ways:
        1. By specifying both width and height
        2. By specifying either width or height (preserving aspect ratio)
        3. By specifying a scale factor
        
        Returns:
            Path to the resized image
        """
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_resized{file_ext}"
        
        # Read the image using OpenCV
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Failed to read image: {input_path}")
        
        # Get original dimensions
        orig_height, orig_width = img.shape[:2]
        
        # Determine interpolation method
        interpolation_methods = {
            'nearest': cv2.INTER_NEAREST,
            'linear': cv2.INTER_LINEAR,
            'area': cv2.INTER_AREA,
            'cubic': cv2.INTER_CUBIC,
            'lanczos': cv2.INTER_LANCZOS4
        }
        
        if interpolation not in interpolation_methods:
            raise ValueError(f"Invalid interpolation method. Choose from: {', '.join(interpolation_methods.keys())}")
        
        interp = interpolation_methods[interpolation]
        
        # Calculate target dimensions
        if scale_factor is not None:
            # Resize by scale factor
            target_width = int(orig_width * scale_factor)
            target_height = int(orig_height * scale_factor)
        elif width is not None and height is not None:
            # Resize to specific dimensions
            target_width = width
            target_height = height
        elif width is not None:
            # Resize to specific width, maintain aspect ratio
            target_width = width
            target_height = int(orig_height * (width / orig_width))
        elif height is not None:
            # Resize to specific height, maintain aspect ratio
            target_height = height
            target_width = int(orig_width * (height / orig_height))
        else:
            raise ValueError("Must provide either width, height, or scale_factor")
        
        # Resize the image
        resized_img = cv2.resize(img, (target_width, target_height), interpolation=interp)
        
        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Save the resized image
        cv2.imwrite(output_path, resized_img)
            
        return output_path