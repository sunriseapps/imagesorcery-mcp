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
        Performs Optical Character Recognition (OCR) on an image using PaddleOCR.

        This tool extracts text from images in various languages. The default language is English,
        but you can specify other languages using their language codes (e.g., 'en', 'ru', 'fr', etc.).
        PaddleOCR supports a wide range of languages including English, Chinese, Japanese, Korean,
        French, German, Italian, Spanish, Portuguese, Russian, Arabic, and many more.

        Returns:
            Dictionary containing the input image path and a list of detected text segments
            with their text content, confidence scores, and bounding box coordinates.
        """
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        try:
            # Import here to avoid loading paddleocr if not needed
            from paddleocr import PaddleOCR
            
            # Normalize language code to lowercase
            lang_code = language.lower().strip()
            
            # Common language code mappings for PaddleOCR
            # This is a more comprehensive mapping that covers most common languages
            language_map = {
                # Latin script languages
                'en': 'en',           # English
                'fr': 'fr',           # French
                'it': 'it',           # Italian
                'es': 'es',           # Spanish
                'pt': 'pt',           # Portuguese
                'de': 'german',       # German
                'nl': 'dutch',        # Dutch
                'sv': 'swedish',      # Swedish
                'no': 'norwegian',    # Norwegian
                'da': 'danish',       # Danish
                'fi': 'finnish',      # Finnish
                'pl': 'polish',       # Polish
                'cs': 'czech',        # Czech
                'sk': 'slovak',       # Slovak
                'hu': 'hungarian',    # Hungarian
                'ro': 'romanian',     # Romanian
                
                # Cyrillic script languages
                'ru': 'ru',           # Russian
                'uk': 'ukrainian',    # Ukrainian
                'bg': 'bulgarian',    # Bulgarian
                'sr': 'serbian',      # Serbian
                'mk': 'macedonian',   # Macedonian
                
                # Asian languages
                'zh': 'ch',           # Chinese (simplified)
                'zh-tw': 'chinese_cht', # Chinese (traditional)
                'ja': 'japan',        # Japanese
                'ko': 'korean',       # Korean
                'th': 'thai',         # Thai
                'vi': 'vietnam',      # Vietnamese
                
                # Other scripts
                'ar': 'arabic',       # Arabic
                'hi': 'hindi',        # Hindi
                'ta': 'ta',           # Tamil
                'te': 'te',           # Telugu
                'he': 'hebrew',       # Hebrew
                'tr': 'turkish',      # Turkish
            }
            
            # Try to get the appropriate language code for PaddleOCR
            paddle_lang = language_map.get(lang_code)
            
            # If language not found in mapping, use the original code
            # PaddleOCR will raise an error if the language is not supported
            if paddle_lang is None:
                paddle_lang = lang_code
            
            # Initialize PaddleOCR with the specified language
            ocr = PaddleOCR(use_angle_cls=True, lang=paddle_lang)
            
            # Perform OCR on the image
            result = ocr.ocr(input_path, cls=True)
            
            # Process results
            text_segments = []
            
            # Handle the PaddleOCR result format
            if result and len(result) > 0:
                for line in result[0]:
                    if len(line) >= 2:  # Make sure we have both bbox and text+confidence
                        bbox = line[0]  # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                        text_info = line[1]  # (text, confidence)
                        
                        # Extract text and confidence
                        text = text_info[0]
                        confidence = float(text_info[1])
                        
                        # Convert bbox to [x1, y1, x2, y2] format
                        x_coords = [point[0] for point in bbox]
                        y_coords = [point[1] for point in bbox]
                        x1, y1 = min(x_coords), min(y_coords)
                        x2, y2 = max(x_coords), max(y_coords)
                        
                        text_segments.append({
                            "text": text,
                            "confidence": confidence,
                            "bbox": [float(x1), float(y1), float(x2), float(y2)]
                        })
            
            return {"image_path": input_path, "text_segments": text_segments}

        except ImportError:
            error_msg = (
                "PaddleOCR is not installed. "
                "Please install it first using: "
                "pip install paddleocr paddlepaddle"
            )
            raise RuntimeError(error_msg) from None
        except Exception as e:
            # Provide more helpful error message
            error_msg = f"Error performing OCR: {str(e)}\n"

            if "not found" in str(e).lower() and "language" in str(e).lower():
                error_msg += (
                    f"The language '{language}' is not supported or the language model "
                    f"could not be found. Please check available languages in PaddleOCR documentation.\n"
                    f"Supported languages include: English (en), Chinese (ch), French (fr), German (de), "
                    f"Japanese (ja), Korean (ko), Italian (it), Spanish (es), Portuguese (pt), "
                    f"Russian (ru), Arabic (ar), and more."
                )
            elif "permission denied" in str(e).lower():
                error_msg += (
                    "Permission denied when trying to access the image file.\n"
                    "Try running the command with appropriate permissions."
                )

            raise RuntimeError(error_msg) from e