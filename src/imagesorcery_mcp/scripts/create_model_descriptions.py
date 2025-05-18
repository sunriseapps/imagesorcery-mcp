#!/usr/bin/env python3
"""
Script to create model descriptions JSON file.
This script should be run during project setup to ensure model descriptions are available.
"""

import json
import os
from pathlib import Path

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def create_model_descriptions():
    """Create a JSON file with model descriptions in the models directory."""
    logger.info(f"Creating model descriptions JSON file at {Path('models') / 'model_descriptions.json'}")
    # YOLOv8 model descriptions
    model_descriptions = {
        "yolo11n.pt": "Ultralytics YOLO11 model for Object Detection. Provides state-of-the-art performance, suitable for tasks requiring a balance of speed and accuracy (smallest of YOLO11).",
        "yolo11s.pt": "Ultralytics YOLO11 model for Object Detection. Provides state-of-the-art performance, more accurate than 'n', with slightly lower speed.",
        "yolo11m.pt": "Ultralytics YOLO11 model for Object Detection. Provides state-of-the-art performance, a medium option balancing accuracy and speed.",
        "yolo11l.pt": "Ultralytics YOLO11 model for Object Detection. Provides state-of-the-art performance, more accurate than 'm', with slightly lower speed.",
        "yolo11x.pt": "Ultralytics YOLO11 model for Object Detection. Provides state-of-the-art performance (highest accuracy of YOLO11 Detect).",
        "yolo11n-seg.pt": "Ultralytics YOLO11 model for Instance Segmentation. Provides state-of-the-art performance, smallest and fastest of YOLO11 Seg.",
        "yolo11s-seg.pt": "Ultralytics YOLO11 model for Instance Segmentation. Provides state-of-the-art performance, a larger variant than 'n'.",
        "yolo11m-seg.pt": "Ultralytics YOLO11 model for Instance Segmentation. Provides state-of-the-art performance, a medium variant.",
        "yolo11l-seg.pt": "Ultralytics YOLO11 model for Instance Segmentation. Provides state-of-the-art performance, a larger variant than 'm'.",
        "yolo11x-seg.pt": "Ultralytics YOLO11 model for Instance Segmentation. Provides state-of-the-art performance (highest accuracy of YOLO11 Seg).",
        "yolo11n-pose.pt": "Ultralytics YOLO11 model for Pose Estimation / Keypoints detection. Provides state-of-the-art performance, smallest and fastest of YOLO11 Pose.",
        "yolo11s-pose.pt": "Ultralytics YOLO11 model for Pose Estimation / Keypoints detection. Provides state-of-the-art performance, a larger variant than 'n'.",
        "yolo11m-pose.pt": "Ultralytics YOLO11 model for Pose Estimation / Keypoints detection. Provides state-of-the-art performance, a medium variant.",
        "yolo11l-pose.pt": "Ultralytics YOLO11 model for Pose Estimation / Keypoints detection. Provides state-of-the-art performance, a larger variant than 'm'.",
        "yolo11x-pose.pt": "Ultralytics YOLO11 model for Pose Estimation / Keypoints detection. Provides state-of-the-art performance (highest accuracy of YOLO11 Pose).",
        "yolo11n-obb.pt": "Ultralytics YOLO11 model for Oriented Object Detection (OBB). Provides state-of-the-art performance, smallest of YOLO11 OBB.",
        "yolo11s-obb.pt": "Ultralytics YOLO11 model for Oriented Object Detection (OBB). Provides state-of-the-art performance, a larger variant than 'n'.",
        "yolo11m-obb.pt": "Ultralytics YOLO11 model for Oriented Object Detection (OBB). Provides state-of-the-art performance, a medium variant.",
        "yolo11l-obb.pt": "Ultralytics YOLO11 model for Oriented Object Detection (OBB). Provides state-of-the-art performance, a larger variant than 'm'.",
        "yolo11x-obb.pt": "Ultralytics YOLO11 model for Oriented Object Detection (OBB). Provides state-of-the-art performance (highest accuracy of YOLO11 OBB).",
        "yolo11n-cls.pt": "Ultralytics YOLO11 model for Image Classification. Provides state-of-the-art performance, smallest of YOLO11 Classify.",
        "yolo11s-cls.pt": "Ultralytics YOLO11 model for Image Classification. Provides state-of-the-art performance, a larger variant than 'n'.",
        "yolo11m-cls.pt": "Ultralytics YOLO11 model for Image Classification. Provides state-of-the-art performance, a medium variant.",
        "yolo11l-cls.pt": "Ultralytics YOLO11 model for Image Classification. Provides state-of-the-art performance, a larger variant than 'm'.",
        "yolo11x-cls.pt": "Ultralytics YOLO11 model for Image Classification. Provides state-of-the-art performance (highest accuracy of YOLO11 Classify).",
        "yolov8n.pt": "General-purpose real-time Ultralytics YOLOv8 model for Object Detection. Provides a good balance of accuracy and speed, suitable for resource-constrained tasks (smallest of YOLOv8 Detect).",
        "yolov8s.pt": "General-purpose real-time Ultralytics YOLOv8 model for Object Detection. Balances accuracy and speed, a larger variant than 'n'.",
        "yolov8m.pt": "General-purpose real-time Ultralytics YOLOv8 model for Object Detection. Balances accuracy and speed, a medium variant.",
        "yolov8l.pt": "General-purpose real-time Ultralytics YOLOv8 model for Object Detection. Balances accuracy and speed, a larger variant than 'm'.",
        "yolov8x.pt": "General-purpose real-time Ultralytics YOLOv8 model for Object Detection. Balances accuracy and speed (highest accuracy of YOLOv8 Detect).",
        "yolov8n-seg.pt": "General-purpose real-time Ultralytics YOLOv8 model for Instance Segmentation. Provides a good balance of accuracy and speed, suitable for resource-constrained tasks (smallest of YOLOv8 Seg).",
        "yolov8s-seg.pt": "General-purpose real-time Ultralytics YOLOv8 model for Instance Segmentation. Balances accuracy and speed, a larger variant than 'n'.",
        "yolov8m-seg.pt": "General-purpose real-time Ultralytics YOLOv8 model for Instance Segmentation. Balances accuracy and speed, a medium variant.",
        "yolov8l-seg.pt": "General-purpose real-time Ultralytics YOLOv8 model for Instance Segmentation. Balances accuracy and speed, a larger variant than 'm'.",
        "yolov8x-seg.pt": "General-purpose real-time Ultralytics YOLOv8 model for Instance Segmentation. Balances accuracy and speed (highest accuracy of YOLOv8 Seg).",
        "yolov8n-pose.pt": "General-purpose real-time Ultralytics YOLOv8 model for Pose Estimation / Keypoints detection. Suitable for resource-constrained tasks (smallest of YOLOv8 Pose).",
        "yolov8s-pose.pt": "General-purpose real-time Ultralytics YOLOv8 model for Pose Estimation / Keypoints detection. A larger variant than 'n'.",
        "yolov8m-pose.pt": "General-purpose real-time Ultralytics YOLOv8 model for Pose Estimation / Keypoints detection. A medium variant.",
        "yolov8l-pose.pt": "General-purpose real-time Ultralytics YOLOv8 model for Pose Estimation / Keypoints detection. A larger variant than 'm'.",
        "yolov8x-pose.pt": "General-purpose real-time Ultralytics YOLOv8 model for Pose Estimation / Keypoints detection. The largest variant.",
        "yolov8x-pose-p6.pt": "General-purpose real-time Ultralytics YOLOv8 model for Pose Estimation / Keypoints detection. Trained with 1280 input size.",
        "yolov8n-obb.pt": "General-purpose real-time Ultralytics YOLOv8 model for Oriented Object Detection (OBB). Suitable for resource-constrained tasks (smallest of YOLOv8 OBB).",
        "yolov8s-obb.pt": "General-purpose real-time Ultralytics YOLOv8 model for Oriented Object Detection (OBB). A larger variant than 'n'.",
        "yolov8m-obb.pt": "General-purpose real-time Ultralytics YOLOv8 model for Oriented Object Detection (OBB). A medium variant.",
        "yolov8l-obb.pt": "General-purpose real-time Ultralytics YOLOv8 model for Oriented Object Detection (OBB). A larger variant than 'm'.",
        "yolov8x-obb.pt": "General-purpose real-time Ultralytics YOLOv8 model for Oriented Object Detection (OBB). The largest variant.",
        "yolov8n-cls.pt": "General-purpose real-time Ultralytics YOLOv8 model for Image Classification. Suitable for resource-constrained tasks (smallest of YOLOv8 Classify).",
        "yolov8s-cls.pt": "General-purpose real-time Ultralytics YOLOv8 model for Image Classification. A larger variant than 'n'.",
        "yolov8m-cls.pt": "General-purpose real-time Ultralytics YOLOv8 model for Image Classification. A medium variant.",
        "yolov8l-cls.pt": "General-purpose real-time Ultralytics YOLOv8 model for Image Classification. A larger variant than 'm'.",
        "yolov8x-cls.pt": "General-purpose real-time Ultralytics YOLOv8 model for Image Classification. The largest variant.",
        "rtdetr-l.pt": "Realtime Detection Transformer (RT-DETR) by Baidu for Object Detection. Well-suited for applications requiring high accuracy and real-time performance (smaller variant).",
        "rtdetr-x.pt": "Realtime Detection Transformer (RT-DETR) by Baidu for Object Detection. Well-suited for applications requiring high accuracy and real-time performance (larger variant).",
        "sam_b.pt": "Segment Anything Model (SAM) by Meta. Provides unique automatic segmentation capabilities based on prompts.",
        "sam2_t.pt": "Segment Anything Model 2 (SAM2) by Meta. The next generation of SAM for video and images, provides automatic segmentation capabilities (smaller variant).",
        "sam2_b.pt": "Segment Anything Model 2 (SAM2) by Meta. The next generation of SAM for video and images, provides automatic segmentation capabilities (larger variant).",
        "mobile_sam.pt": "Mobile Segment Anything Model (MobileSAM). A mobile variant of SAM for segmentation.",
        "FastSAM-s.pt": "Fast Segment Anything Model (FastSAM). A segmentation model that is faster and more efficient than SAM. Supports segmentation based on text prompts or bounding boxes.",
        "yolo_nas_s.pt": "YOLO-NAS model (based on Neural Architecture Search) for Object Detection. Optimized for resource-constrained environments and focused on efficiency (smallest).",
        "yolo_nas_m.pt": "YOLO-NAS model (based on Neural Architecture Search) for Object Detection. Offers a balanced approach, suitable for general object detection with higher accuracy (medium).",
        "yolo_nas_l.pt": "YOLO-NAS model (based on Neural Architecture Search) for Object Detection. Designed for scenarios requiring the highest accuracy, where computational resources are less constrained (largest).",
        "yolov8s-world.pt": "YOLO-World model (based on YOLOv8) for Real-Time Open-Vocabulary Object Detection. Detects any objects based on text descriptions, effective for zero-shot tasks (smaller variant, no export support).",
        "yolov8s-worldv2.pt": "YOLO-World V2 model (based on YOLOv8) for Real-Time Open-Vocabulary Object Detection. Detects any objects based on text descriptions, effective for zero-shot tasks (smaller variant, with export support and deterministic training). Recommended for custom training.",
        "yolov8m-world.pt": "YOLO-World model (based on YOLOv8) for Real-Time Open-Vocabulary Object Detection. Detects any objects based on text descriptions, effective for zero-shot tasks (medium variant, no export support).",
        "yolov8m-worldv2.pt": "YOLO-World V2 model (based on YOLOv8) for Real-Time Open-Vocabulary Object Detection. Detects any objects based on text descriptions, effective for zero-shot tasks (medium variant, with export support and deterministic training).",
        "yolov8l-world.pt": "YOLO-World model (based on YOLOv8) for Real-Time Open-Vocabulary Object Detection. Detects any objects based on text descriptions, effective for zero-shot tasks (larger variant, no export support).",
        "yolov8l-worldv2.pt": "YOLO-World V2 model (based on YOLOv8) for Real-Time Open-Vocabulary Object Detection. Detects any objects based on text descriptions, effective for zero-shot tasks (larger variant, with export support and deterministic training).",
        "yolov8x-world.pt": "YOLO-World model (based on YOLOv8) for Real-Time Open-Vocabulary Object Detection. Detects any objects based on text descriptions, effective for zero-shot tasks (largest variant, no export support).",
        "yolov8x-worldv2.pt": "YOLO-World V2 model (based on YOLOv8) for Real-Time Open-Vocabulary Object Detection. Detects any objects based on text descriptions, effective for zero-shot tasks (largest variant, with export support and deterministic training).",
        "yoloe-11s-seg.pt": "Real-Time Open-Vocabulary YOLOE model for Instance Segmentation. Detects arbitrary classes using text/visual prompts (smallest).",
        "yoloe-11m-seg.pt": "Real-Time Open-Vocabulary YOLOE model for Instance Segmentation. Detects arbitrary classes using text/visual prompts (medium).",
        "yoloe-11l-seg.pt": "Real-Time Open-Vocabulary YOLOE model for Instance Segmentation. Detects arbitrary classes using text/visual prompts (largest).",
        "yoloe-v8s-seg.pt": "Real-Time Open-Vocabulary YOLOE model (based on YOLOv8) for Instance Segmentation. Detects arbitrary classes using text/visual prompts (smallest).",
        "yoloe-v8m-seg.pt": "Real-Time Open-Vocabulary YOLOE model (based on YOLOv8) for Instance Segmentation. Detects arbitrary classes using text/visual prompts (medium).",
        "yoloe-v8l-seg.pt": "Real-Time Open-Vocabulary YOLOE model (based on YOLOv8) for Instance Segmentation. Detects arbitrary classes using text/visual prompts (largest).",
        "yoloe-11s-seg-pf.pt": "Real-Time Open-Vocabulary Prompt-Free YOLOE model for Instance Segmentation. Detects objects from a large built-in vocabulary (smallest).",
        "yoloe-11m-seg-pf.pt": "Real-Time Open-Vocabulary Prompt-Free YOLOE model for Instance Segmentation. Detects objects from a large built-in vocabulary (medium).",
        "yoloe-11l-seg-pf.pt": "Real-Time Open-Vocabulary Prompt-Free YOLOE model for Instance Segmentation. Detects objects from a large built-in vocabulary (largest).",
        "yoloe-v8s-seg-pf.pt": "Real-Time Open-Vocabulary Prompt-Free YOLOE model (based on YOLOv8) for Instance Segmentation. Detects objects from a large built-in vocabulary (smallest).",
        "yoloe-v8m-seg-pf.pt": "Real-Time Open-Vocabulary Prompt-Free YOLOE model (based on YOLOv8) for Instance Segmentation. Detects objects from a large built-in vocabulary (medium).",
        "yoloe-v8l-seg-pf.pt": "Real-Time Open-Vocabulary Prompt-Free YOLOE model (based on YOLOv8) for Instance Segmentation. Detects objects from a large built-in vocabulary (largest).",
        "yolov10n.pt": "Real-Time End-to-End YOLOv10 model for Object Detection. Suitable for very resource-constrained environments (smallest).",
        "yolov10s.pt": "Real-Time End-to-End YOLOv10 model for Object Detection. Balances speed and accuracy.",
        "yolov10m.pt": "Real-Time End-to-End YOLOv10 model for Object Detection. Suitable for general use (medium).",
        "yolov10l.pt": "Real-Time End-to-End YOLOv10 model for Object Detection. High accuracy at the cost of computational resources.",
        "yolov10x.pt": "Real-Time End-to-End YOLOv10 model for Object Detection. Maximum accuracy and performance (largest).",
        "yolov3u.pt": "YOLOv3 model for Object Detection. An older but effective real-time model.",
        "yolov3-tinyu.pt": "YOLOv3-Tiny model for Object Detection. A very fast, lightweight version of YOLOv3.",
        "yolov3-sppu.pt": "YOLOv3-SPP model for Object Detection. A version of YOLOv3 with an SPP module for improved performance.",
        "yolov9t.pt": "YOLOv9 model for Object Detection. Uses PGI for data preservation, useful for lightweight models (smallest of YOLOv9 Detect).",
        "yolov9s.pt": "YOLOv9 model for Object Detection. Uses PGI for data preservation, useful for lightweight models (a larger variant than 't').",
        "yolov9m.pt": "YOLOv9 model for Object Detection. Uses PGI for data preservation, useful for lightweight models (medium).",
        "yolov9c.pt": "YOLOv9 model for Object Detection. Uses PGI for data preservation, useful for lightweight models (a larger variant than 'm').",
        "yolov9e.pt": "YOLOv9 model for Object Detection. Uses PGI for data preservation, useful for lightweight models (largest of YOLOv9 Detect).",
        "yolov9c-seg.pt": "YOLOv9 model for Instance Segmentation. Uses PGI for data preservation, useful for lightweight models (smaller variant).",
        "yolov9e-seg.pt": "YOLOv9 model for Instance Segmentation. Uses PGI for data preservation, useful for lightweight models (larger variant).",
        "yolo12n.pt": "YOLO12 'Attention-Centric' model for Object Detection. (Example provided only for the 'n' variant)."
    }

    # Create models directory if it doesn't exist
    models_dir = Path("models").resolve()
    os.makedirs(models_dir, exist_ok=True)
    logger.info(f"Ensured models directory exists: {models_dir}")

    descriptions_file = models_dir / "model_descriptions.json"
    existing_descriptions = {}

    # Read existing descriptions if the file exists
    if descriptions_file.exists():
        try:
            with open(descriptions_file, "r") as f:
                existing_descriptions = json.load(f)
            logger.info(f"Loaded existing model descriptions from: {descriptions_file}")
        except json.JSONDecodeError:
            logger.warning(f"Error decoding JSON from {descriptions_file}, starting with empty descriptions.")
            existing_descriptions = {}
        except Exception as e:
            logger.error(f"Error reading existing model descriptions from {descriptions_file}: {e}")
            existing_descriptions = {}

    # Merge new descriptions with existing ones
    # Existing descriptions take precedence to avoid overwriting custom ones
    merged_descriptions = model_descriptions.copy()
    merged_descriptions.update(existing_descriptions)

    # Write merged descriptions to JSON file
    logger.info(f"Writing merged model descriptions to: {descriptions_file}")
    try:
        with open(descriptions_file, "w") as f:
            json.dump(merged_descriptions, f, indent=2)
        logger.info(f"Model descriptions updated successfully at: {descriptions_file}")
        print(f"✅ Model descriptions updated at: {descriptions_file}")
        return str(descriptions_file)
    except Exception as e:
        logger.error(f"Error writing merged model descriptions to {descriptions_file}: {e}")
        print(f"❌ Failed to update model descriptions at: {descriptions_file}")
        return None


def main():
    logger.info(f"Running create_model_descriptions script from {Path(__file__).resolve()}")
    create_model_descriptions()
    logger.info("create_model_descriptions script finished")


if __name__ == "__main__":
    main()
