import os
from typing import Annotated, Dict, List, Union

from fastmcp import FastMCP
from pydantic import Field


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def ocr(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
        language: Annotated[
            str,
            Field(
                description="Language code for OCR (e.g., 'en', 'ru', 'fr', etc.)",
            ),
        ] = "en",  # Default language is English
    ) -> Dict[str, Union[str, List[Dict[str, Union[str, float, List[float]]]]]]:
        """
        Performs Optical Character Recognition (OCR) on an image using EasyOCR.

        This tool extracts text from images in various languages. The default language is English,
        but you can specify other languages using their language codes (e.g., 'en', 'ru', 'fr', etc.).

        Returns:
            Dictionary containing the input image path and a list of detected text segments
            with their text content, confidence scores, and bounding box coordinates.
        """
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        try:
            # Import here to avoid loading easyocr if not needed
            import easyocr

            # Create reader with specified language
            reader = easyocr.Reader([language])

            # Perform OCR on the image
            results = reader.readtext(input_path)

            # Process results
            text_segments = []
            for result in results:
                # EasyOCR can return results in different formats depending on the version
                # Handle both possible formats
                if len(result) == 3:
                    # Format: (bbox, text, confidence)
                    bbox, text, confidence = result
                elif len(result) == 4:
                    # Format: (bbox, text, confidence, _)
                    bbox, text, confidence, _ = result
                else:
                    # Unknown format, try to extract what we can
                    bbox = result[0] if len(result) > 0 else [[0, 0], [0, 0], [0, 0], [0, 0]]
                    text = result[1] if len(result) > 1 else ""
                    confidence = result[2] if len(result) > 2 else 0.0

                # EasyOCR returns bounding box as 4 points (top-left, top-right, bottom-right, bottom-left)
                # Convert to [x1, y1, x2, y2] format (top-left and bottom-right corners)
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                x1, y1 = min(x_coords), min(y_coords)
                x2, y2 = max(x_coords), max(y_coords)

                text_segments.append(
                    {
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": [float(x1), float(y1), float(x2), float(y2)]
                    }
                )

            return {"image_path": input_path, "text_segments": text_segments}

        except ImportError:
            error_msg = (
                "EasyOCR is not installed. "
                "Please install it first using: "
                "pip install easyocr"
            )
            raise RuntimeError(error_msg) from None
        except Exception as e:
            # Provide more helpful error message
            error_msg = f"Error performing OCR: {str(e)}\n"

            if "not found" in str(e).lower() and "language" in str(e).lower():
                error_msg += (
                    f"The language '{language}' is not supported or the language model "
                    f"could not be found. Please check available languages in EasyOCR documentation."
                )
            elif "permission denied" in str(e).lower():
                error_msg += (
                    "Permission denied when trying to access the image file.\n"
                    "Try running the command with appropriate permissions."
                )

            raise RuntimeError(error_msg) from e