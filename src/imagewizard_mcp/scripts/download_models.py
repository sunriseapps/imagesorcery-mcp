#!/usr/bin/env python3
"""
Script to download YOLOv8 models for offline use.
This script should be run during project setup to ensure models are available.
"""

import argparse
import os
import shutil
import sys
from pathlib import Path


def get_models_dir():
    """Get the models directory in the project root."""
    models_dir = Path("models")
    os.makedirs(models_dir, exist_ok=True)
    return str(models_dir)


def download_model(model_size):
    """Download a specific YOLOv8 model to the models directory."""
    try:
        # Set up the model name
        model_name = f"yolov8{model_size}.pt"

        # Get the models directory
        models_dir = get_models_dir()
        model_path = os.path.join(models_dir, model_name)

        # Check if model already exists in models directory
        if os.path.exists(model_path):
            print(f"✅ Model already exists at: {model_path}")
            return True

        # Set environment variable to use the models directory
        os.environ["YOLO_CONFIG_DIR"] = models_dir

        # Import and download the model
        from ultralytics import YOLO

        print(f"Downloading YOLOv8{model_size} model...")

        # The model variable is used to trigger the download
        model = YOLO(model_name)  # noqa: F841

        # Check if the model was downloaded to the expected location
        if os.path.exists(model_path):
            print(f"✅ Model successfully downloaded to: {model_path}")
            return True

        # Check if model was downloaded to current directory
        current_dir_model = Path(model_name)
        if current_dir_model.exists():
            print(f"✅ Model found in current directory: {current_dir_model}")
            try:
                # Move the model to the models directory
                shutil.move(str(current_dir_model), model_path)
                print(f"✅ Model moved to: {model_path}")
                return True
            except Exception as e:
                print(f"⚠️ Could not move model: {e}")
                print(f"✅ You can still use the model from: {current_dir_model}")
                return True

        # If not found in expected locations,
        # try to find it in ultralytics default location
        possible_locations = [
            Path.home() / ".ultralytics" / "weights" / model_name,
            Path(os.path.dirname(os.path.abspath(__file__))) / "weights" / model_name,
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
                print(f"✅ Model found at a different location: {loc}")
                try:
                    shutil.copy(loc, model_path)
                    print(f"✅ Model copied to: {model_path}")
                    return True
                except Exception as e:
                    print(f"⚠️ Could not copy model: {e}")
                    print(
                        f"❌ Please manually copy the model from {loc} to {model_path}"
                    )
                    return False

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
