import os
from pathlib import Path
from typing import Annotated, Dict, List, Union

from fastmcp import FastMCP
from pydantic import Field


def get_model_path(model_name):
    """Get the path to a model in the models directory."""
    model_path = Path("models") / model_name
    if model_path.exists():
        return str(model_path)
    return None


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def detect(
        input_path: Annotated[str, Field(description="Path to the input image")],
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
                description="Model name to use for detection (e.g., 'yoloe-11s-seg.pt', 'yolov8m.pt')",
            ),
        ] = "yoloe-11l-seg.pt",  # Default model
    ) -> Dict[str, Union[str, List[Dict[str, Union[str, float, List[float]]]]]]:
        """
        Detect objects in an image using models from Ultralytics.

        This tool requires pre-downloaded models. Use the download-yolo-models
        command to download models before using this tool.

        Returns:
            Dictionary containing the input image path and a list of detected objects
            with their class names, confidence scores, and bounding box coordinates.
        """
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Add .pt extension if it doesn't exist
        if not model_name.endswith(".pt"):
            model_name = f"{model_name}.pt"

        # Try to find the model
        model_path = get_model_path(model_name)

        # If model not found, raise an error with helpful message
        if not model_path:
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

            # Import here to avoid loading ultralytics if not needed
            from ultralytics import YOLO

            # Load the model from the found path
            model = YOLO(model_path)

            # Run inference on the image
            results = model(input_path, conf=confidence)[0]

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

            return {"image_path": input_path, "detections": detections}

        except Exception as e:
            # Provide more helpful error message
            error_msg = f"Error running object detection: {str(e)}\n"

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
