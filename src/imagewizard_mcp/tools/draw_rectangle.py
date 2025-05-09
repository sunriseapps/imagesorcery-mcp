import os
from typing import Annotated, Any, Dict, List, Optional

import cv2
from fastmcp import FastMCP
from pydantic import Field


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def draw_rectangles(
        input_path: Annotated[str, Field(description="Path to the input image")],
        rectangles: Annotated[
            List[Dict[str, Any]],
            Field(
                description=(
                    "List of rectangle items to draw. Each item should have: "
                    "'x1' (int), 'y1' (int), 'x2' (int), 'y2' (int), and optionally "
                    "'color' (list of 3 ints [B,G,R]), "
                    "'thickness' (int), 'filled' (bool)"
                )
            ),
        ],
        output_path: Annotated[
            Optional[str],
            Field(
                description=(
                    "Path to save the output image. "
                    "If not provided, will use input filename "
                    "with '_with_rectangles' suffix."
                )
            ),
        ] = None,
    ) -> str:
        """
        Draw rectangles on an image using OpenCV.
        
        This tool allows adding multiple rectangles to an image with customizable
        position, color, thickness, and fill option.
        
        Each rectangle is defined by two points: (x1, y1) for the top-left corner
        and (x2, y2) for the bottom-right corner.
        
        Returns:
            Path to the image with drawn rectangles
        """
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_with_rectangles{file_ext}"

        # Read the image using OpenCV
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Failed to read image: {input_path}")

        # Draw each rectangle on the image
        for rect_item in rectangles:
            # Extract rectangle coordinates (required)
            x1 = rect_item["x1"]
            y1 = rect_item["y1"]
            x2 = rect_item["x2"]
            y2 = rect_item["y2"]
            
            # Extract optional parameters with defaults
            color = rect_item.get("color", [0, 0, 0])  # Default: black
            thickness = rect_item.get("thickness", 1)
            filled = rect_item.get("filled", False)
            
            # If filled is True, set thickness to -1 (OpenCV's way of filling shapes)
            if filled:
                thickness = -1
            
            # Draw the rectangle on the image
            cv2.rectangle(
                img, 
                (x1, y1), 
                (x2, y2), 
                color, 
                thickness
            )

        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save the image with rectangles
        cv2.imwrite(output_path, img)

        return output_path