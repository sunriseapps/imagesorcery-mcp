#!/usr/bin/env python3
"""
Script to download YOLO compatible models for offline use.
This script should be run during project setup to ensure models are available.
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

import requests
from tqdm import tqdm


def get_models_dir():
    """Get the models directory in the project root."""
    models_dir = Path("models")
    os.makedirs(models_dir, exist_ok=True)
    return str(models_dir)


def download_from_url(url, output_path):
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


def download_from_huggingface(model_name):
    """Download a model from Hugging Face."""
    # Extract repo_id and model filename
    if "/" not in model_name:
        print("❌ Invalid Hugging Face model format. Use 'username/repo:filename' or 'username/repo'")
        return False
    
    parts = model_name.split(":", 1)
    repo_id = parts[0]
    filename = parts[1] if len(parts) > 1 else None
    
    # Default description
    model_description = f"Model from Hugging Face repository: {repo_id}"
    
    # Try to get model description
    try:
        from huggingface_hub import model_info
        info = model_info(repo_id)
        if info.cardData and "model-index" in info.cardData:
            model_index = info.cardData["model-index"]
            if model_index and len(model_index) > 0 and "name" in model_index[0]:
                model_description = model_index[0].get('name', model_description)
                print(f"📝 Model description: {model_description}")
        elif info.description:
            # Extract first line or first 100 characters of description
            description = info.description.split('\n')[0][:100]
            if len(info.description) > 100:
                description += "..."
            model_description = description
            print(f"📝 Model description: {model_description}")
    except Exception as e:
        print(f"⚠️ Could not fetch model description: {str(e)}")
    
    # If no specific filename provided, try to find a .pt file
    if filename is None:
        try:
            from huggingface_hub import list_repo_files
            files = list_repo_files(repo_id)
            pt_files = [f for f in files if f.endswith('.pt')]
            if not pt_files:
                print(f"❌ No .pt files found in {repo_id}")
                return False
            filename = pt_files[0]
            print(f"✅ Found model file in repository: {filename}")
        except Exception as e:
            print(f"❌ Error listing files in repository: {str(e)}")
            return False
    
    # Create directory structure based on repo_id
    models_dir = get_models_dir()
    repo_dir = os.path.join(models_dir, repo_id.replace("/", os.sep))
    os.makedirs(repo_dir, exist_ok=True)
    
    # Set the output path
    output_filename = os.path.basename(filename)
    output_path = os.path.join(repo_dir, output_filename)
    
    # Update model_descriptions.json with the model description
    model_key = f"{repo_id}/{output_filename}"
    update_model_description(model_key, model_description)
    
    # Check if model already exists
    if os.path.exists(output_path):
        print(f"✅ Model already exists at: {output_path}")
        return True
    
    # Construct the download URL
    url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
    
    print(f"Downloading from Hugging Face: {repo_id}/{filename}")
    print(f"Saving to: {output_path}")
    return download_from_url(url, output_path)


def update_model_description(model_key, description):
    """Update the model_descriptions.json file with a new model description."""
    models_dir = get_models_dir()
    descriptions_file = os.path.join(models_dir, "model_descriptions.json")
    
    # Load existing descriptions or create new if file doesn't exist
    if os.path.exists(descriptions_file):
        try:
            with open(descriptions_file, 'r') as f:
                descriptions = json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Error reading model_descriptions.json, creating new file")
            descriptions = {}
    else:
        descriptions = {}
    
    # Update the description for this model
    if model_key not in descriptions:
        descriptions[model_key] = description
        print(f"✅ Added description for {model_key} to model_descriptions.json")
    elif descriptions[model_key] != description:
        descriptions[model_key] = description
        print(f"✅ Updated description for {model_key} in model_descriptions.json")
    
    # Save the updated descriptions
    try:
        with open(descriptions_file, 'w') as f:
            json.dump(descriptions, f, indent=2, sort_keys=True)
    except Exception as e:
        print(f"⚠️ Error updating model_descriptions.json: {str(e)}")

def download_ultralytics_model(model_name):
    """Download a specific YOLO model from Ultralytics to the models directory."""
    try:
        # Get the models directory
        models_dir = get_models_dir()
        
        # Set the output path
        output_path = os.path.join(models_dir, model_name)
        
        # Check if model already exists in models directory
        if os.path.exists(output_path):
            print(f"✅ Model already exists at: {output_path}")
            return True

        # Set environment variable to use the models directory
        os.environ["YOLO_CONFIG_DIR"] = models_dir

        # Import and download the model
        from ultralytics import YOLO

        print(f"Downloading {model_name} model...")

        # The model variable is used to trigger the download
        model = YOLO(model_name)  # noqa: F841

        # Check if the model was downloaded to the expected location
        if os.path.exists(output_path):
            print(f"✅ Model successfully downloaded to: {output_path}")
            return True

        # Check if model was downloaded to current directory
        current_dir_model = Path(model_name)
        if current_dir_model.exists():
            print(f"✅ Model found in current directory: {current_dir_model}")
            try:
                # Move the model to the models directory
                shutil.move(str(current_dir_model), output_path)
                print(f"✅ Model moved to: {output_path}")
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
                    shutil.copy(loc, output_path)
                    print(f"✅ Model copied to: {output_path}")
                    return True
                except Exception as e:
                    print(f"⚠️ Could not copy model: {e}")
                    print(
                        f"❌ Please manually copy the model from {loc} to {output_path}"
                    )
                    return False

        print(f"❌ Failed to download model to expected path: {output_path}")
        return False

    except Exception as e:
        print(f"❌ Error downloading model: {str(e)}")
        return False


def download_model(model_name, source=None):
    """
    Legacy function for backward compatibility.
    Downloads a model from the specified source.
    """
    if source == "ultralytics":
        return download_ultralytics_model(model_name)
    elif source == "huggingface":
        return download_from_huggingface(model_name)
    else:
        print(f"❌ Unknown model source: {source}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download YOLO compatible models for offline use"
    )
    
    # Create a mutually exclusive group for the model sources
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--ultralytics",
        metavar="MODEL_NAME",
        help="Download a model from Ultralytics (e.g., 'yolov8m.pt')"
    )
    source_group.add_argument(
        "--huggingface",
        metavar="REPO_ID[:FILENAME]",
        help="Download a model from Hugging Face (e.g., 'username/repo:model.pt' or 'username/repo')"
    )

    args = parser.parse_args()
    
    if args.ultralytics:
        success = download_ultralytics_model(args.ultralytics)
    elif args.huggingface:
        success = download_from_huggingface(args.huggingface)
    else:
        # This should never happen due to the required=True in the mutually_exclusive_group
        print("❌ No model source specified")
        success = False
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
