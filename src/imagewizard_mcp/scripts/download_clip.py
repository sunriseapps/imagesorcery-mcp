#!/usr/bin/env python3
"""
Script to download CLIP models required for YOLOe text prompts.
"""

import os
import sys
from pathlib import Path

import requests
from tqdm import tqdm


def get_models_dir():
    """Get the models directory in the project root."""
    models_dir = Path("models")
    os.makedirs(models_dir, exist_ok=True)
    return models_dir


def download_file(url, output_path):
    """Download a file from a URL with progress bar."""
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
        
        return True
    except Exception as e:
        print(f"❌ Error downloading from {url}: {str(e)}")
        return False


def check_clip_installed():
    """Check if CLIP is installed."""
    try:
        import clip  # noqa: F401
        return True
    except ImportError:
        return False


def install_clip():
    """Install CLIP from the Ultralytics GitHub repository."""
    print("⚠️ CLIP is not installed. Attempting to install...")
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "git+https://github.com/ultralytics/CLIP.git"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print("✅ CLIP installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install CLIP: {e}")
        print(e.stdout)
        print(e.stderr)
        return False


def download_clip_model():
    """Download the MobileCLIP model required for YOLOe text prompts."""
    models_dir = get_models_dir()
    clip_model_path = models_dir / "mobileclip_blt.ts"
    root_clip_model_path = Path("mobileclip_blt.ts")
    
    # Check if model already exists in either location
    if clip_model_path.exists() and root_clip_model_path.exists():
        print(f"✅ CLIP model already exists at: {clip_model_path} and {root_clip_model_path}")
        return True
    
    # URL for the MobileCLIP model
    url = "https://github.com/ultralytics/assets/releases/download/v8.3.0/mobileclip_blt.ts"
    
    # Download to models directory
    if not clip_model_path.exists():
        print(f"Downloading CLIP model to models directory from: {url}")
        success_models = download_file(url, clip_model_path)
        if success_models:
            print(f"✅ CLIP model successfully downloaded to: {clip_model_path}")
        else:
            print(f"❌ Failed to download CLIP model to: {clip_model_path}")
            return False
    
    # Download or copy to root directory
    if not root_clip_model_path.exists():
        if clip_model_path.exists():
            # Copy from models directory to root
            import shutil
            print(f"Copying CLIP model from {clip_model_path} to {root_clip_model_path}")
            shutil.copy(clip_model_path, root_clip_model_path)
            print(f"✅ CLIP model successfully copied to: {root_clip_model_path}")
        else:
            # Download directly to root
            print(f"Downloading CLIP model to root directory from: {url}")
            success_root = download_file(url, root_clip_model_path)
            if success_root:
                print(f"✅ CLIP model successfully downloaded to: {root_clip_model_path}")
            else:
                print(f"❌ Failed to download CLIP model to: {root_clip_model_path}")
                return False
    
    return True

def main():
    """Main function to download CLIP models."""
    print("Downloading CLIP models required for YOLOe text prompts...")
    
    # First, check if CLIP is installed
    if not check_clip_installed():
        if not install_clip():
            print("❌ Failed to install CLIP. Please install it manually with:")
            print("pip install git+https://github.com/ultralytics/CLIP.git")
            sys.exit(1)
    
    # Then download the MobileCLIP model
    if download_clip_model():
        print("✅ All CLIP models downloaded successfully")
    else:
        print("❌ Failed to download all required CLIP models")
        sys.exit(1)


if __name__ == "__main__":
    main()
