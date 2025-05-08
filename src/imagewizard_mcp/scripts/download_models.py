#!/usr/bin/env python3
"""
Script to download YOLOv8 models for offline use.
This script should be run during project setup to ensure models are available.
"""

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path


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


def download_model(model_size):
    """Download a specific YOLOv8 model to a temporary directory."""
    try:
        # Set up the model name
        model_name = f"yolov8{model_size}.pt"

        # Get the temporary directory
        temp_dir = get_temp_weights_dir()
        model_path = os.path.join(temp_dir, model_name)

        # Check if model already exists
        if os.path.exists(model_path):
            print(f"✅ Model already exists at: {model_path}")
            return True

        # Set environment variable to use the temp directory
        os.environ["YOLO_CONFIG_DIR"] = temp_dir

        # Import and download the model
        from ultralytics import YOLO

        print(f"Downloading YOLOv8{model_size} model...")
        YOLO(model_name)

        # Check if the model was downloaded to the expected location
        if os.path.exists(model_path):
            print(f"✅ Model successfully downloaded to: {model_path}")
            return True

        # If not in the expected location, try to find it and copy it
        found_path = find_model(model_name)
        if found_path and found_path != model_path:
            print(f"✅ Model found at a different location: {found_path}")
            try:
                shutil.copy(found_path, model_path)
                print(f"✅ Model copied to: {model_path}")
                return True
            except Exception as e:
                print(f"⚠️ Could not copy model: {e}")
                print(f"✅ You can still use the model from: {found_path}")
                return True

        print(f"❌ Failed to download model to expected path: {model_path}")
        return False

    except Exception as e:
        print(f"❌ Error downloading model: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download YOLOv8 models for offline use"
    )
    parser.add_argument(
        "--model-size",
        choices=["n", "s", "m", "l", "x"],
        default="m",
        help="Model size to download (default: m)",
    )
    parser.add_argument("--all", action="store_true", help="Download all model sizes")

    args = parser.parse_args()

    if args.all:
        success = True
        for size in ["n", "s", "m", "l", "x"]:
            if not download_model(size):
                success = False

        if not success:
            sys.exit(1)
    else:
        if not download_model(args.model_size):
            sys.exit(1)


if __name__ == "__main__":
    main()
