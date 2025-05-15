import os
from pathlib import Path
from typing import Annotated, Dict, List, Union

from fastmcp import FastMCP
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def get_model_path(model_name):
    """Get the path to a model in the models directory."""
    logger.info(f"Attempting to get path for model: {model_name}")
    model_path = Path("models") / model_name
    if model_path.exists():
        logger.info(f"Model found at: {model_path}")
        return str(model_path)
    logger.warning(f"Model not found in models directory: {model_name}")
    return None


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def detect(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
        confidence: Annotated[
            float,
            Field(
                description="Confidence threshold for detection (0.0 to 1.0)",
                ge=0.0,
                le=1.0,
            ),
        ] = 0.75,
        model_name: Annotated[
            str,
            Field(
                description="Model name to use for detection (e.g., 'yoloe-11l-seg-pf.pt', 'yolov8m.pt')",
            ),
        ] = "yoloe-11l-seg-pf.pt",  # Default model
    ) -> Dict[str, Union[str, List[Dict[str, Union[str, float, List[float]]]]]]:
        """
        Detect objects in an image using models from Ultralytics.

        This tool requires pre-downloaded models. Use the download-yolo-models
        command to download models before using this tool.

        If objects aren't common, consider using a specialized model.

        Returns:
            Dictionary containing the input image path and a list of detected objects
            with their class names, confidence scores, and bounding box coordinates.
        """
        logger.info(f"Detect tool requested for image: {input_path} with model: {model_name} and confidence: {confidence}")

        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        # Add .pt extension if it doesn't exist
        if not model_name.endswith(".pt"):
            original_model_name = model_name
            model_name = f"{model_name}.pt"
            logger.info(f"Added .pt extension to model name: {original_model_name} -> {model_name}")

        # Try to find the model
        model_path = get_model_path(model_name)

        # If model not found, raise an error with helpful message
        if not model_path:
            logger.error(f"Model {model_name} not found.")
            # List available models
            available_models = []
            models_dir = Path("models")
            
            # Find all .pt files in the models directory and its subdirectories
            if models_dir.exists():
                for file in models_dir.glob("**/*.pt"):
                    available_models.append(str(file.relative_to(models_dir)))

            error_msg = (
                f"Model {model_name} not found. "
                f"Available local models: "
                f"{', '.join(available_models) if available_models else 'None'}\n"
                "To use this tool, you need to download the model first using:\n"
                "download-yolo-models --ultralytics MODEL_NAME\n"
                "or\n"
                "download-yolo-models --huggingface REPO_ID[:FILENAME]\n"
                "Models will be downloaded to the 'models' directory "
                "in the project root."
            )
            raise RuntimeError(error_msg)

        try:
            # Set environment variable to use the models directory
            os.environ["YOLO_CONFIG_DIR"] = str(Path("models").absolute())
            logger.info(f"Set YOLO_CONFIG_DIR environment variable to: {os.environ['YOLO_CONFIG_DIR']}")

            # Import here to avoid loading ultralytics if not needed
            logger.info("Importing Ultralytics")
            from ultralytics import YOLO
            logger.info("Ultralytics imported successfully")

            # Load the model from the found path
            logger.info(f"Loading model from: {model_path}")
            model = YOLO(model_path)
            logger.info("Model loaded successfully")

            # Run inference on the image
            logger.info(f"Running inference on {input_path} with confidence {confidence}")
            results = model(input_path, conf=confidence)[0]
            logger.info(f"Inference completed. Found {len(results.boxes)} detections.")

            # Process results
            detections = []
            for box in results.boxes:
                # Get class name
                class_id = int(box.cls.item())
                class_name = results.names[class_id]

                # Get confidence score
                conf = float(box.conf.item())

                # Get bounding box coordinates (x1, y1, x2, y2)
                x1, y1, x2, y2 = [float(coord) for coord in box.xyxy[0].tolist()]

                detections.append(
                    {"class": class_name, "confidence": conf, "bbox": [x1, y1, x2, y2]}
                )
                logger.debug(f"Detected: class={class_name}, confidence={conf:.2f}, bbox=[{x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f}]")

            logger.info(f"Detection completed successfully for {input_path}")
            return {"image_path": input_path, "detections": detections}

        except Exception as e:
            # Provide more helpful error message
            error_msg = f"Error running object detection: {str(e)}\n"
            logger.error(f"Error during object detection: {str(e)}", exc_info=True)

            if "not found" in str(e).lower():
                error_msg += (
                    "The model could not be found. "
                    "Please download it first using: "
                    "download-yolo-models --ultralytics MODEL_NAME"
                )
            elif "permission denied" in str(e).lower():
                error_msg += (
                    "Permission denied when trying to access or create the models "
                    "directory.\n"
                    "Try running the command with appropriate permissions."
                )

            raise RuntimeError(error_msg) from e
