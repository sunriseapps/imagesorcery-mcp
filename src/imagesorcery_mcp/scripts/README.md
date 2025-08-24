# 🪄 ImageSorcery MCP Server Scripts Documentation

This document provides detailed information about each script available in the 🪄 ImageSorcery MCP Server, including their purpose, arguments, and examples of how to use them.

## Overview

The scripts directory contains utility scripts for model management and setup within the 🪄 ImageSorcery MCP Server. These scripts handle tasks such as:

- `download-models`: Downloading YOLO models from various sources
- `create-model-descriptions`: Creating model descriptions (used in `setup.sh`)
- `download-clip-models`: Downloading CLIP models required for text-based detection (YOLOe *-pf models) (used in `setup.sh`)
- `post-install-imagesorcery`: Running all post-installation tasks in a single command
- `populate_telemetry_keys.py` / `clear_telemetry_keys.py`: build-time helpers for telemetry keys management

These scripts are typically run during project setup, packaging, or when adding new models to the system.

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
  - Places the model in the root directory where it's expected by the find tool
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
  - Ensures a `.user_id` file exists in project root (used for telemetry user identification).
- **Usage:** Run directly, through the server with the `--post-install` flag, or through the provided command-line entry point.

**Command-line Usage:**
```bash
# Run post-installation as a standalone script
python -m src.imagesorcery_mcp.scripts.post_install

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

## Telemetry Keys Management (build-time)

Telemetry keys are no longer stored in `telemetry.toml`. Instead, telemetry API keys are managed via a small Python module and/or environment variables:

- Telemetry user identifier is stored in `.user_id` (created by `post_install.py`).
- API keys are provided either via environment variables or the Python module:
  - Environment variables (preferred during build/deploy):
    - `IMAGESORCERY_AMPLITUDE_API_KEY`
    - `IMAGESORCERY_POSTHOG_API_KEY`
  - Fallback module (kept in the repository as empty defaults): `src/imagesorcery_mcp/telemetry_keys.py`
    - Contains `AMPLITUDE_API_KEY = ""` and `POSTHOG_API_KEY = ""`

Rationale:
- `telemetry.toml` was unreliable in some packaging/build scenarios (it could be omitted from final artifacts). Using environment variables (and a small Python module as a fallback) ensures keys are available at runtime and during build without embedding secrets in the repo.

### `populate_telemetry_keys.py`

**Purpose**: Populate `src/imagesorcery_mcp/telemetry_keys.py` with API keys from the environment (or `.env`) during build time if desired.

**Functionality**:
- Reads `IMAGESORCERY_AMPLITUDE_API_KEY` and `IMAGESORCERY_POSTHOG_API_KEY` from environment variables (or `.env` when python-dotenv is available)
- Writes these values into `src/imagesorcery_mcp/telemetry_keys.py`
- Intended to be used in CI/build pipelines where keys are injected as environment variables before packaging

**Command-line Usage**:
```bash
python -m src.imagesorcery_mcp.scripts.populate_telemetry_keys
```

**Notes**:
- The script will not commit changes; CI should handle any necessary cleanup.
- To skip population, set `SKIP_TELEMETRY_POPULATION=true`.

### `clear_telemetry_keys.py`

**Purpose**: Clear API keys in `src/imagesorcery_mcp/telemetry_keys.py` after build to keep the repository clean.

**Functionality**:
- Overwrites `src/imagesorcery_mcp/telemetry_keys.py` with empty string defaults:
  ```py
  AMPLITUDE_API_KEY = ""
  POSTHOG_API_KEY = ""
  ```
- Intended to be invoked as a post-build/cleanup step in CI

**Command-line Usage**:
```bash
python -m src.imagesorcery_mcp.scripts.clear_telemetry_keys
```

### Recommended CI / Build Integration

A suggested pipeline for safely using telemetry keys in CI:

1. In CI, set environment variables:
   - `IMAGESORCERY_AMPLITUDE_API_KEY` and `IMAGESORCERY_POSTHOG_API_KEY`
2. Run the populate script:
   - `python -m src.imagesorcery_mcp.scripts.populate_telemetry_keys`
3. Build/package the project
4. Run the clear script to remove keys from the working copy:
   - `python -m src.imagesorcery_mcp.scripts.clear_telemetry_keys`
5. Ensure the CI does not persist telemetry_keys.py with real keys in any artifact or commit.

**Dependencies**:
- `python-dotenv` (optional) — used by scripts to load a `.env` file when present

**Error Handling**:
- Scripts log errors and return non-zero exit codes on failure so CI can fail fast.
