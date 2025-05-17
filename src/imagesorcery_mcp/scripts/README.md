# 🪄 ImageSorcery MCP Server Scripts Documentation

This document provides detailed information about each script available in the 🪄 ImageSorcery MCP Server, including their purpose, arguments, and examples of how to use them.

## Overview

The scripts directory contains utility scripts for model management and setup within the 🪄 ImageSorcery MCP Server. These scripts handle tasks such as:

- `download-models`: Downloading YOLO models from various sources
- `create-model-descriptions`: Creating model descriptions (used in `setup.sh`)
- `download-clip-models`: Downloading CLIP models required for text-based detection (YOLOe *-pf models) (used in `setup.sh`)
- `post-install-imagesorcery`: Running all post-installation tasks in a single command

These scripts are typically run during project setup or when adding new models to the system.

## Common Functions

These scripts share some common functions and patterns:

- All scripts use a central logger from `imagesorcery_mcp.logging_config`
- They typically create the `models` directory if it doesn't exist
- They handle existing files to avoid unnecessary downloads
- Progress bars are provided for downloads using `tqdm`

## Available Scripts

### `download_models.py`

Downloads YOLO compatible models for offline use from either Ultralytics or Hugging Face.

- **Purpose:** Ensures that required detection models are available for tools like `detect` and `find`.
- **Functionality:**
  - Downloads models from Ultralytics repositories
  - Downloads models from Hugging Face repositories
  - Updates the model descriptions JSON file with information about downloaded models
  - Organizes models in a proper directory structure
- **Arguments:**
  - `--ultralytics MODEL_NAME`: Download a model from Ultralytics (e.g., 'yolov8m.pt')
  - `--huggingface REPO_ID[:FILENAME]`: Download a model from Hugging Face (e.g., 'username/repo:model.pt')

**Command-line Usage:**
```bash
# Download from Ultralytics
download-yolo-models --ultralytics yolov8m.pt

# Download from Hugging Face
download-yolo-models --huggingface ultralytics/yolov8:yolov8m.pt
```

**Python Import Usage:**
```python
from imagesorcery_mcp.scripts.download_models import download_ultralytics_model, download_from_huggingface

# Download from Ultralytics
success = download_ultralytics_model('yolov8m.pt')

# Download from Hugging Face
success = download_from_huggingface('ultralytics/yolov8:yolov8m.pt')
```

#### Notes

- Downloaded models are stored in the `models` directory, which is included in `.gitignore` to prevent large model files from being committed to the repository.
- If you encounter permission issues when running these scripts, ensure you have the necessary write access to the project directory.

### `create_model_descriptions.py`

Creates a JSON file containing descriptions for various detection models in the models directory.

- **Purpose:** Ensures that model description information is available for reference by tools and users.
- **Functionality:** 
  - Creates a comprehensive list of model descriptions for various YOLO models (YOLOv8, YOLO11, YOLO-NAS, etc.)
  - Merges new descriptions with any existing ones, preserving custom descriptions
  - Writes the merged descriptions to `models/model_descriptions.json`
- **Usage:** Run directly or through the provided command-line entry point.

**Command-line Usage:**
```bash
create-model-descriptions
```

**Python Import Usage:**
```python
from imagesorcery_mcp.scripts.create_model_descriptions import create_model_descriptions

# Create the model descriptions file
result_path = create_model_descriptions()
```

### `download_clip.py`

Downloads the MobileCLIP model required for YOLOe text prompts functionality.

- **Purpose:** Ensures that the required MobileCLIP model is available for text-based detection in the `find` tool.
- **Functionality:**
  - Downloads the MobileCLIP model required for YOLOe text prompts
  - Places the model in both the models directory and root directory for compatibility
- **Usage:** Run directly or through the provided command-line entry point.

**Command-line Usage:**
```bash
download-clip-models
```

**Python Import Usage:**
```python
from imagesorcery_mcp.scripts.download_clip import download_clip_model

# Download CLIP model
success = download_clip_model()
```

### `post_install.py`

Runs all post-installation tasks for the ImageSorcery MCP server in a single command.

- **Purpose:** Automates the complete setup process after package installation.
- **Functionality:**
  - Creates the models directory
  - Generates the model descriptions file with `create-model-descriptions`
  - Downloads default YOLO models (yoloe-11l-seg-pf.pt, yoloe-11s-seg-pf.pt, yoloe-11l-seg.pt, yoloe-11s-seg.pt) with `download-yolo-models`
  - Installs the `clip` Python package from Ultralytics' GitHub repository.
  - Downloads the required CLIP model file for text prompts with `download-clip-models`.
- **Usage:** Run directly, through the server with the `--post-install` flag, or through the provided command-line entry point.

**Command-line Usage:**
```bash
# Run post-installation as a standalone script
post-install-imagesorcery

# Or run it through the server with the --post-install flag
imagesorcery-mcp --post-install
```

**Python Import Usage:**
```python
from imagesorcery_mcp.scripts.post_install import run_post_install

# Run all post-installation tasks
success = run_post_install()
if success:
    print("Post-installation completed successfully!")
else:
    print("Post-installation failed.")
```

## Example Workflow

A typical workflow for setting up the 🪄 ImageSorcery MCP server with all required models:

```bash
# Option 1: Complete setup with a single command
imagesorcery-mcp --post-install

# Option 2: Manual step-by-step setup
# 1. Create model descriptions
create-model-descriptions

# 2. Download required YOLO models
download-yolo-models --ultralytics yoloe-11l-seg-pf.pt
download-yolo-models --ultralytics yoloe-11s-seg-pf.pt
download-yolo-models --ultralytics yoloe-11l-seg.pt
download-yolo-models --ultralytics yoloe-11s-seg.pt

# 3. Download CLIP models for text prompts
download-clip-models
```

The `--post-install` flag is designed to automate all these steps and is the recommended approach for initial setup.
