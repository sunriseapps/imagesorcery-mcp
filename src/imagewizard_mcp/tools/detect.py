import os
import shutil
import tempfile
from pathlib import Path
from typing import Annotated, Dict, List, Union

from fastmcp import FastMCP
from pydantic import Field


# Check if we're online
def is_online():
    try:
        # Try to connect to a reliable server
        import socket

        socket.create_connection(("1.1.1.1", 53), timeout=3)
        return True
    except OSError:
        return False


def get_temp_weights_dir():
    """Get a temporary directory for storing weights that is guaranteed to be
    writable.
    """
    temp_dir = Path(tempfile.gettempdir()) / "ultralytics_weights"
    os.makedirs(temp_dir, exist_ok=True)
    return str(temp_dir)


def find_model(model_name):
    """Find a model file in common locations."""
    # Try to find the model in common locations
    possible_locations = [
        Path.home() / ".ultralytics" / "weights" / model_name,
        Path(os.path.dirname(os.path.abspath(__file__))) / "weights" / model_name,
        Path.cwd() / "weights" / model_name,
        Path(tempfile.gettempdir()) / "ultralytics_weights" / model_name,
    ]

    # Try to import ultralytics to find its location
    try:
        import ultralytics

        ultralytics_dir = Path(ultralytics.__file__).parent
        possible_locations.append(ultralytics_dir / "weights" / model_name)
    except ImportError:
        pass

    # Check each location
    for loc in possible_locations:
        if loc.exists():
            return str(loc)

    # If not found in common locations, try a recursive search (limited depth)
    try:
        # Search in home directory (limited to .ultralytics folder)
        home_models = list(Path.home().glob(f".ultralytics/**/{model_name}"))
        if home_models:
            return str(home_models[0])

        # Search in current directory (limited depth)
        cwd_models = list(Path.cwd().glob(f"**/{model_name}"))
        if cwd_models:
            return str(cwd_models[0])
    except Exception:
        pass

    return None


def download_model_to_temp(model_name):
    """Download a model to a temporary directory."""
    try:
        # Create a temporary directory for the model
        temp_dir = get_temp_weights_dir()
        model_path = os.path.join(temp_dir, model_name)

        # Check if model already exists in temp directory
        if os.path.exists(model_path):
            return model_path

        # Set environment variable to use the temp directory
        os.environ["YOLO_CONFIG_DIR"] = temp_dir

        # Import and download the model
        from ultralytics import YOLO

        YOLO(model_name)

        # Check if the model was downloaded to the expected location
        if os.path.exists(model_path):
            return model_path

        # If not in the expected location, try to find it and copy it
        found_path = find_model(model_name)
        if found_path and found_path != model_path:
            shutil.copy(found_path, model_path)
            return model_path

        return found_path
    except Exception as e:
        print(f"Error downloading model to temp: {e}")
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
        offline_mode: Annotated[
            bool,
            Field(
                description=(
                    "If True, will not attempt to download model if not available"
                    " locally"
                )
            ),
        ] = False,
    ) -> Dict[str, Union[str, List[Dict[str, Union[str, float, List[float]]]]]]:
        """
        Detect objects in an image using YOLOv8 from Ultralytics.

        The function uses the YOLOv8 model to detect objects in the image and returns
        information about the detected objects including class name, confidence score,
        and bounding box coordinates.

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
            raise ValueError(
                f"Invalid model size. Must be one of: {', '.join(valid_sizes)}"
            )

        # Construct model name
        model_name = f"yolov8{model_size}.pt"

        # Try to find the model
        model_path = find_model(model_name)

        # If model not found and we're not in offline mode, try to download it to temp
        if not model_path and not offline_mode and is_online():
            model_path = download_model_to_temp(model_name)

        # If we're in offline mode or actually offline, and model not found
        if (offline_mode or not is_online()) and not model_path:
            # List available models
            available_models = []

            # Try to find any YOLOv8 models
            for size in valid_sizes:
                found_model = find_model(f"yolov8{size}.pt")
                if found_model:
                    available_models.append(os.path.basename(found_model))

            error_msg = (
                f"Model {model_name} not found locally and cannot be downloaded in"
                " offline mode.\n"
                "Available local models: "
                f"{', '.join(available_models) if available_models else 'None'}\n"
                "To use this tool, you need to:\n"
                "1. Connect to the internet, or\n"
                "2. Pre-download the model using: python -c \"from ultralytics import"
                " YOLO; YOLO('yolov8m.pt')\"\n"
                "   (Replace 'yolov8m.pt' with your desired model size: n, s, m, l, x)"
            )
            raise RuntimeError(error_msg)

        try:
            # Set environment variable to use the temp directory
            temp_dir = get_temp_weights_dir()
            os.environ["YOLO_CONFIG_DIR"] = temp_dir

            # Import here to avoid loading ultralytics if not needed
            from ultralytics import YOLO

            # Load the YOLOv8 model
            # If model_path is found, use it directly, otherwise let YOLO handle it
            model = YOLO(model_path if model_path else model_name)

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

            if "not online" in str(e).lower() or "download failure" in str(e).lower():
                error_msg += (
                    "The model could not be downloaded because you are offline.\n"
                    "Try using offline_mode=True with a pre-downloaded model, or"
                    " connect to the internet."
                )
            elif "permission denied" in str(e).lower():
                error_msg += (
                    "Permission denied when trying to access or create the weights"
                    " directory.\n"
                    "Try running the command with appropriate permissions or specify a"
                    " different directory."
                )

            raise RuntimeError(error_msg) from e
