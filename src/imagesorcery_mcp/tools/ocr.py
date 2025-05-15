import os
from typing import Annotated, Dict, List, Union

from fastmcp import FastMCP
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


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
        logger.info(f"OCR requested for image: {input_path} with language: {language}")
        
        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        try:
            # Import here to avoid loading dependencies if not needed
            import cv2
            import easyocr
            
            logger.info("EasyOCR imported successfully")

            # Read the image
            logger.info(f"Reading image from: {input_path}")
            img = cv2.imread(input_path)
            if img is None:
                logger.error(f"Failed to read image: {input_path}")
                raise ValueError(f"Failed to read image: {input_path}. The file may be corrupted or not an image.")
            
            # Check image dimensions and convert to grayscale
            logger.info(f"Image shape: {img.shape}")
            if len(img.shape) == 3:
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                logger.info(f"Converted image to grayscale: {img_gray.shape}")
            else:
                img_gray = img
                logger.info("Image is already grayscale")

            # Create reader with specified language
            logger.info(f"Creating EasyOCR reader for language: {language}")
            reader = easyocr.Reader([language])
            logger.info("EasyOCR reader created successfully")

            # Perform OCR directly on the numpy array
            logger.info("Starting OCR processing on image array")
            results = reader.readtext(img_gray)  # Pass the numpy array directly
            logger.info(f"OCR processing completed with {len(results)} text segments found")

            # Process results
            text_segments = []
            for i, result in enumerate(results):
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
                    logger.warning(f"Unexpected result format for segment {i}: {result}")
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
                logger.debug(f"Processed segment {i}: text='{text[:30]}...' confidence={confidence:.2f}")

            logger.info(f"OCR completed successfully for {input_path}")
            return {"image_path": input_path, "text_segments": text_segments}

        except ImportError as e:
            if "easyocr" in str(e).lower():
                error_msg = (
                    "EasyOCR is not installed. "
                    "Please install it first using: "
                    "pip install easyocr"
                )
            elif "cv2" in str(e).lower():
                error_msg = (
                    "OpenCV (cv2) is not installed. "
                    "Please install it first using: "
                    "pip install opencv-python"
                )
            else:
                error_msg = f"Required dependency not installed: {str(e)}"
            
            logger.error(f"Import error: {error_msg}")
            raise RuntimeError(error_msg) from None
        except Exception as e:
            # Provide more helpful error message
            error_msg = f"Error performing OCR: {str(e)}\n"

            if "not found" in str(e).lower() and "language" in str(e).lower():
                error_msg += (
                    f"The language '{language}' is not supported or the language model "
                    f"could not be found. Please check available languages in EasyOCR documentation."
                )
                logger.error(f"Language not supported: {language}")
            elif "permission denied" in str(e).lower():
                error_msg += (
                    "Permission denied when trying to access the image file.\n"
                    "Try running the command with appropriate permissions."
                )
                logger.error(f"Permission denied accessing file: {input_path}")
            else:
                logger.error(f"OCR processing error: {str(e)}", exc_info=True)

            raise RuntimeError(error_msg) from e
