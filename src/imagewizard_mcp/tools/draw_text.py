import os
from typing import Annotated, Any, Dict, List, Optional

import cv2
from fastmcp import FastMCP
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def draw_texts(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
        texts: Annotated[
            List[Dict[str, Any]],
            Field(
                description=(
                    "List of text items to draw. Each item should have: "
                    "'text' (string), 'x' (int), 'y' (int), and optionally "
                    "'font_scale' (float), 'color' (list of 3 ints [B,G,R]), "
                    "'thickness' (int), 'font_face' (string)"
                )
            ),
        ],
        output_path: Annotated[
            Optional[str],
            Field(
                description=(
                    "Full path to save the output image (must be a full path). "
                    "If not provided, will use input filename "
                    "with '_with_text' suffix."
                )
            ),
        ] = None,
    ) -> str:
        """
        Draw text on an image using OpenCV.
        
        This tool allows adding multiple text elements to an image with customizable
        position, font, size, color, and thickness.
        
        Available font_face options:
        - 'FONT_HERSHEY_SIMPLEX' (default)
        - 'FONT_HERSHEY_PLAIN'
        - 'FONT_HERSHEY_DUPLEX'
        - 'FONT_HERSHEY_COMPLEX'
        - 'FONT_HERSHEY_TRIPLEX'
        - 'FONT_HERSHEY_COMPLEX_SMALL'
        - 'FONT_HERSHEY_SCRIPT_SIMPLEX'
        - 'FONT_HERSHEY_SCRIPT_COMPLEX'
        
        Returns:
            Path to the image with drawn text
        """
        logger.info(f"Draw texts tool requested for image: {input_path} with {len(texts)} text items")

        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_with_text{file_ext}"
            logger.info(f"Output path not provided, generated: {output_path}")

        # Read the image using OpenCV
        logger.info(f"Reading image: {input_path}")
        img = cv2.imread(input_path)
        if img is None:
            logger.error(f"Failed to read image: {input_path}")
            raise ValueError(f"Failed to read image: {input_path}")
        logger.info(f"Image read successfully. Shape: {img.shape}")

        # Font face mapping
        font_faces = {
            "FONT_HERSHEY_SIMPLEX": cv2.FONT_HERSHEY_SIMPLEX,
            "FONT_HERSHEY_PLAIN": cv2.FONT_HERSHEY_PLAIN,
            "FONT_HERSHEY_DUPLEX": cv2.FONT_HERSHEY_DUPLEX,
            "FONT_HERSHEY_COMPLEX": cv2.FONT_HERSHEY_COMPLEX,
            "FONT_HERSHEY_TRIPLEX": cv2.FONT_HERSHEY_TRIPLEX,
            "FONT_HERSHEY_COMPLEX_SMALL": cv2.FONT_HERSHEY_COMPLEX_SMALL,
            "FONT_HERSHEY_SCRIPT_SIMPLEX": cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
            "FONT_HERSHEY_SCRIPT_COMPLEX": cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
        }
        logger.debug("OpenCV font face mapping created")

        # Draw each text item on the image
        for i, text_item in enumerate(texts):
            # Extract text and position (required)
            text = text_item["text"]
            x = text_item["x"]
            y = text_item["y"]
            
            # Extract optional parameters with defaults
            font_scale = text_item.get("font_scale", 1.0)
            color = text_item.get("color", [0, 0, 0])  # Default: black
            thickness = text_item.get("thickness", 1)
            
            # Get font face (default to SIMPLEX if not specified or invalid)
            font_face_name = text_item.get("font_face", "FONT_HERSHEY_SIMPLEX")
            font_face = font_faces.get(font_face_name, cv2.FONT_HERSHEY_SIMPLEX)
            
            logger.debug(f"Drawing text {i+1}: '{text}' at ({x}, {y}) with font_scale={font_scale}, color={color}, thickness={thickness}, font_face={font_face_name}")

            # Draw the text on the image
            cv2.putText(
                img, 
                text, 
                (x, y), 
                font_face, 
                font_scale, 
                color, 
                thickness
            )
            logger.debug(f"Text {i+1} drawn")

        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            logger.info(f"Output directory does not exist, creating: {output_dir}")
            os.makedirs(output_dir)
            logger.info(f"Output directory created: {output_dir}")

        # Save the image with text
        logger.info(f"Saving image with text to: {output_path}")
        cv2.imwrite(output_path, img)
        logger.info(f"Image with text saved successfully to: {output_path}")

        return output_path
