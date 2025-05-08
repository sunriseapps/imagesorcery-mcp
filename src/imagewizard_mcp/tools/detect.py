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
        ] = 0.25,
        model_size: Annotated[
            str,
            Field(
                description="YOLOv8 model size: 'n', 's', 'm', 'l', or 'x'",
            ),
        ] = "m",
    ) -> Dict[str, Union[str, List[Dict[str, Union[str, float, List[float]]]]]]:
        """
        Detect objects in an image using YOLOv8 from Ultralytics.
        
        This tool requires pre-downloaded YOLOv8 models. Use the download-yolo-models
        command to download models before using this tool.
        
        Returns:
            Dictionary containing the input image path and a list of detected objects
            with their class names, confidence scores, and bounding box coordinates.
        """
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Validate model size
        valid_sizes = ["n", "s", "m", "l", "x"]
        if model_size not in valid_sizes:
            raise ValueError(f"Invalid model size. Must be one of: {', '.join(valid_sizes)}")
        
        # Construct model name
        model_name = f"yolov8{model_size}.pt"
        
        # Try to find the model
        model_path = get_model_path(model_name)
        
        # If model not found, raise an error with helpful message
        if not model_path:
            # List available models
            available_models = []
            
            # Try to find any YOLOv8 models
            for size in valid_sizes:
                found_model = get_model_path(f"yolov8{size}.pt")
                if found_model:
                    available_models.append(os.path.basename(found_model))
            
            error_msg = (
                f"Model {model_name} not found. "
                f"Available local models: "
                f"{', '.join(available_models) if available_models else 'None'}\n"
                "To use this tool, you need to download the model first using:\n"
                "download-yolo-models --model-size m\n"
                "Models will be downloaded to the 'models' directory in the project root."
            )
            raise RuntimeError(error_msg)
        
        try:
            # Set environment variable to use the models directory
            os.environ['YOLO_CONFIG_DIR'] = str(Path("models").absolute())
            
            # Import here to avoid loading ultralytics if not needed
            from ultralytics import YOLO
            
            # Load the YOLOv8 model from the found path
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
                
                detections.append({
                    "class": class_name,
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2]
                })
            
            return {
                "image_path": input_path,
                "detections": detections
            }
            
        except Exception as e:
            # Provide more helpful error message
            error_msg = f"Error running object detection: {str(e)}\n"
            
            if "not found" in str(e).lower():
                error_msg += (
                    "The model could not be found. "
                    "Please download it first using: download-yolo-models --model-size m"
                )
            elif "permission denied" in str(e).lower():
                error_msg += (
                    "Permission denied when trying to access or create the models "
                    "directory.\n"
                    "Try running the command with appropriate permissions."
                )
            
            raise RuntimeError(error_msg) from e
