#!/usr/bin/env python3
"""
Script to download CLIP models required for YOLOe text prompts.
"""

import os
import sys
from pathlib import Path

import requests
from tqdm import tqdm

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def get_models_dir():
    """Get the models directory in the project root."""
    models_dir = Path("models").resolve()
    os.makedirs(models_dir, exist_ok=True)
    logger.info(f"Ensured models directory exists: {models_dir}")
    return models_dir


def download_file(url, output_path):
    """Download a file from a URL with progress bar."""
    logger.info(f"Attempting to download file from {url} to {output_path}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        
        with open(output_path, 'wb') as file, tqdm(
            desc=f"Downloading to {os.path.basename(output_path)}",
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(block_size):
                size = file.write(data)
                bar.update(size)
        
        logger.info(f"Successfully downloaded file to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading from {url}: {str(e)}")
        return False


def download_clip_model():
    """Download the MobileCLIP model required for YOLOe text prompts."""
    logger.info("Attempting to download CLIP model")
    root_clip_model_path = Path("mobileclip_blt.ts").resolve()

    # Check if model already exists in root directory
    if root_clip_model_path.exists():
        logger.info(f"CLIP model already exists at: {root_clip_model_path}")
        return True

    # URL for the MobileCLIP model
    url = "https://github.com/ultralytics/assets/releases/download/v8.3.0/mobileclip_blt.ts"

    # Download directly to root directory
    logger.info(f"Downloading CLIP model to root directory from: {url}")
    success = download_file(url, root_clip_model_path)
    if success:
        logger.info(f"CLIP model successfully downloaded to: {root_clip_model_path}")
        return True
    else:
        logger.error(f"Failed to download CLIP model to: {root_clip_model_path}")
        return False


def main():
    """Main function to download CLIP models."""
    logger.info(f"Running download_clip_models script from {Path(__file__).resolve()}")
    
    # Download the MobileCLIP model
    if download_clip_model():
        logger.info("CLIP model downloaded successfully")
        print("✅ CLIP model download completed successfully")
    else:
        logger.error("Failed to download CLIP model")
        print("❌ Failed to download CLIP model")
        sys.exit(1)
    
    logger.info("download_clip_models script finished")


if __name__ == "__main__":
    main()
