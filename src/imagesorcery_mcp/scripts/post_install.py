#!/usr/bin/env python3
"""
Script to run post-installation tasks for imagesorcery-mcp.
This script creates the models directory, model descriptions file,
and downloads default models.
"""

import os
import subprocess # Ensure subprocess is imported
import sys # Ensure sys is imported
from pathlib import Path

# Import the central logger
from imagesorcery_mcp.logging_config import logger
from imagesorcery_mcp.scripts.create_model_descriptions import create_model_descriptions
from imagesorcery_mcp.scripts.download_clip import download_clip_model
from imagesorcery_mcp.scripts.download_models import download_ultralytics_model

def install_clip():
    """Install CLIP from the Ultralytics GitHub repository."""
    logger.info("Installing CLIP package from GitHub...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "git+https://github.com/ultralytics/CLIP.git"],
            check=True,
            stdout=sys.stdout, # Can be replaced with subprocess.PIPE if console output is not needed
            stderr=sys.stderr  # Can be replaced with subprocess.PIPE
        )
        logger.info("CLIP package installed successfully")
        print("✅ CLIP package installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install CLIP: {e}")
        print(f"❌ Failed to install CLIP package: {e}")
        return False
    except FileNotFoundError: # Handle case where pip or python executable is not found
        logger.error("Failed to install CLIP: Python executable or pip not found.")
        print("❌ Failed to install CLIP package: Python executable or pip not found.")
        return False


def run_post_install():
    """Run all post-installation tasks."""
    logger.info(f"Running post-installation tasks from {Path(__file__).resolve()}...")

    # Create models directory
    models_dir = Path("models").resolve()
    os.makedirs(models_dir, exist_ok=True)
    logger.info(f"Created models directory: {models_dir}")

    # Create model descriptions file
    logger.info("Creating model descriptions file...")
    descriptions_file = create_model_descriptions()
    if descriptions_file:
        logger.info(f"Model descriptions file created at: {descriptions_file}")
    else:
        logger.error("Failed to create model descriptions file")
        return False

    # Download default Ultralytics YOLO models
    default_models = [
        "yoloe-11l-seg-pf.pt",
        "yoloe-11s-seg-pf.pt",
        "yoloe-11l-seg.pt",
        "yoloe-11s-seg.pt"
    ]
    
    logger.info("Downloading default Ultralytics YOLO models...")
    for model in default_models:
        logger.info(f"Downloading {model}...")
        success = download_ultralytics_model(model)
        if not success:
            logger.error(f"Failed to download model: {model}")
            return False
    print("✅ Ultralytics YOLO models download completed successfully")

    # Install CLIP package
    logger.info("Installing CLIP package for text prompts...")
    if not install_clip():
        logger.error("Failed to install CLIP package. Text prompt functionality for 'find' tool might be limited.")
        return False
    
    # Download CLIP model
    logger.info("Downloading CLIP model for text prompts...")
    try:
        # Download the CLIP model file
        success = download_clip_model()
        if not success:
            logger.error("Failed to download CLIP model")
            return False
    except Exception as e:
        logger.error(f"Error downloading CLIP model: {str(e)}")
        return False
    print("✅ CLIP model download completed successfully")
    
    logger.info("Post-installation tasks completed successfully!")
    print("✅ Post-installation tasks completed successfully!")
    return True


def main():
    """Main entry point for the post_install script."""
    logger.info(f"Starting post-installation process from {Path(__file__).resolve()}")
    success = run_post_install()
    if not success:
        logger.error("Post-installation process failed")
        sys.exit(1)
    logger.info("Post-installation process completed")


if __name__ == "__main__":
    main()
