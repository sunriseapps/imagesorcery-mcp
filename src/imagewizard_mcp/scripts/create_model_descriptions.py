#!/usr/bin/env python3
"""
Script to create model descriptions JSON file.
This script should be run during project setup to ensure model descriptions are available.
"""

import json
import os
from pathlib import Path


def create_model_descriptions():
    """Create a JSON file with model descriptions in the models directory."""
    # YOLOv8 model descriptions
    model_descriptions = {
        "yolov8n.pt": (
            "YOLOv8 Nano - Smallest and fastest model, suitable for edge devices "
            "with limited resources."
        ),
        "yolov8s.pt": (
            "YOLOv8 Small - Balanced model for applications requiring moderate speed "
            "and accuracy."
        ),
        "yolov8m.pt": (
            "YOLOv8 Medium - Default model with good balance between accuracy "
            "and speed."
        ),
        "yolov8l.pt": (
            "YOLOv8 Large - Higher accuracy model suitable for applications "
            "where precision is important."
        ),
        "yolov8x.pt": (
            "YOLOv8 Extra Large - Highest accuracy model, best for applications "
            "requiring maximum precision."
        ),
    }

    # Create models directory if it doesn't exist
    models_dir = Path("models")
    os.makedirs(models_dir, exist_ok=True)

    # Write descriptions to JSON file
    descriptions_file = models_dir / "model_descriptions.json"
    with open(descriptions_file, "w") as f:
        json.dump(model_descriptions, f, indent=2)

    print(f"✅ Model descriptions created at: {descriptions_file}")
    return str(descriptions_file)


def main():
    create_model_descriptions()


if __name__ == "__main__":
    main()