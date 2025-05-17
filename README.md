# 🪄 ImageSorcery MCP - Powerful Image Processing Tools for AI Assistants

[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT) [![MCP](https://img.shields.io/badge/Protocol-MCP-lightgrey)](https://github.com/microsoft/mcp) [![Claude App](https://img.shields.io/badge/Works_with-Claude_App-purple)](https://claude.ai) [![Cline](https://img.shields.io/badge/Works_with-Cline-orange)](https://github.com/ClineLabs/cline) 


## ❌ Without ImageSorcery MCP

AI assistants are limited when working with images:

- ❌ Can't modify or analyze images directly
- ❌ No ability to crop, resize, or process images
- ❌ Some LLMs can't detect objects or extract text from images
- ❌ Limited to verbal descriptions with no visual manipulation

## ✅ With ImageSorcery MCP

`🪄 ImageSorcery` empowers AI assistants with powerful image processing capabilities:

- ✅ Crop, resize, and rotate images with precision
- ✅ Draw text and shapes on images
- ✅ Detect objects using state-of-the-art models
- ✅ Extract text from images with OCR
- ✅ Get detailed image metadata
- ✅ Use a wide range of pre-trained models for object detection, OCR, and more

Just ask your AI to help with image tasks:

> "Copy all the images with pets from ~/photos/ into ~/pets/."

> "Numerate fields on this screenshot.png and prepare screenshot_description.md with a list of described fields."

> "Crop the photo.jpg to make the person be centered."

😉 _**Hint:** Add "use imagesorcery" to make sure it will uses propper tool"._

Your tool will combine multiple tools listed below to achieve your goal.

## 🛠️ Available Tools

| Tool | Description | Example Prompt |
|------|-------------|----------------|
| `crop` | Crops an image using OpenCV's NumPy slicing approach | "Crop my image 'input.png' from coordinates (10,10) to (200,200) and save it as 'cropped.png'" |
| `resize` | Resizes an image using OpenCV | "Resize my image 'photo.jpg' to 800x600 pixels and save it as 'resized_photo.jpg'" |
| `rotate` | Rotates an image using imutils.rotate_bound function | "Rotate my image 'photo.jpg' by 45 degrees and save it as 'rotated_photo.jpg'" |
| `draw_texts` | Draws text on an image using OpenCV | "Add text 'Hello World' at position (50,50) and 'Copyright 2023' at the bottom right corner of my image 'photo.jpg'" |
| `draw_rectangles` | Draws rectangles on an image using OpenCV | "Draw a red rectangle from (50,50) to (150,100) and a filled blue rectangle from (200,150) to (300,250) on my image 'photo.jpg'" |
| `get_metainfo` | Gets metadata information about an image file | "Get metadata information about my image 'photo.jpg'" |
| `detect` | Detects objects in an image using models from Ultralytics | "Detect objects in my image 'photo.jpg' with a confidence threshold of 0.4" |
| `find` | Finds objects in an image based on a text description | "Find all dogs in my image 'photo.jpg' with a confidence threshold of 0.4" |
| `get_models` | Lists all available models in the models directory | "List all available models in the models directory" |
| `ocr` | Performs Optical Character Recognition (OCR) on an image using EasyOCR | "Extract text from my image 'document.jpg' using OCR with English language" |

😉 _**Hint:** detailed information and usage instructions for each tool can be found in the tool's `/src/imagesorcery_mcp/tools/README.md`._

## 🚀 Getting Started

### Requirements

- `Python 3.10` or higher
- `Claude.app`, `Cline`, or another MCP client

### Installation

1.  **Install the package using pip:**
    It's recommended to use a virtual environment, but you can also install it globally.
    ```bash
    # Optional: Create and activate a virtual environment
    # python -m venv venv
    # source venv/bin/activate  # For Linux/macOS
    # venv\Scripts\activate    # For Windows

    pip install imagesorcery-mcp
    ```

2.  **Run the post-installation script:**
    This step is crucial for downloading the models required by the tools.
    ```bash
    imagesorcery-mcp --post-install
    ```

<details>
<summary>What does the post-installation script do?</summary>
The `imagesorcery-mcp --post-install` script performs the following actions:

- Creates a `models` directory to store pre-trained models.
- Generates the initial `models/model_descriptions.json` file.
- Downloads default YOLO models (`yoloe-11l-seg-pf.pt`, `yoloe-11s-seg-pf.pt`, `yoloe-11l-seg.pt`, `yoloe-11s-seg.pt`) required by the `detect` tool.
- Downloads the CLIP model required by the `find` tool for text prompts (the CLIP Python package is installed as a dependency).

You can run this process anytime to restore the default models.
</details>

## ⚙️ Configuration MCP client

Add to your MCP client these settings.
If `imagesorcery-mcp` is in your system's PATH after installation, you can use `imagesorcery-mcp` directly as the command. Otherwise, you'll need to provide the full path to the executable.

```json
"mcpServers": {
    "imagesorcery-mcp": {
      "command": "imagesorcery-mcp", // Or /full/path/to/venv/bin/imagesorcery-mcp if installed in a venv
      "transportType": "stdio",
      "autoApprove": ["detect", "crop", "get_models", "draw_texts", "get_metainfo", "rotate", "resize", "classify", "draw_rectangles", "find", "ocr"],
      "timeout": 100
    }
}
```

<details>
<summary>For Windows</summary>

```json
"mcpServers": {
    "imagesorcery-mcp": {
      "command": "imagesorcery-mcp.exe", // Or C:\\full\\path\\to\\venv\\Scripts\\imagesorcery-mcp.exe if installed in a venv
      "transportType": "stdio",
      "autoApprove": ["detect", "crop", "get_models", "draw_texts", "get_metainfo", "rotate", "resize", "classify", "draw_rectangles", "find", "ocr"],
      "timeout": 100
    }
}
```
</details>

## 📦 Additional Models

Some tools require specific models to be available in the `models` directory:

```bash
# Download models for the detect tool
download-yolo-models --ultralytics yoloe-11l-seg
download-yolo-models --huggingface ultralytics/yolov8:yolov8m.pt
```

<details>
<summary>About Model Descriptions</summary>

When downloading models, the script automatically updates the `models/model_descriptions.json` file:

- For Ultralytics models: Descriptions are predefined in `src/imagesorcery_mcp/scripts/create_model_descriptions.py` and include detailed information about each model's purpose, size, and characteristics.

- For Hugging Face models: Descriptions are automatically extracted from the model card on Hugging Face Hub. The script attempts to use the model name from the model index or the first line of the description.

After downloading models, it's recommended to check the descriptions in `models/model_descriptions.json` and adjust them if needed to provide more accurate or detailed information about the models' capabilities and use cases.
</details>

## 🤝 Contributing
<details>
<summary>Whether you're a 👤 human or an 🤖 AI agent, we welcome your contributions to this project!</summary>

### Directory Structure

This repository is organized as follows:

```
.
├── .gitignore                 # Specifies intentionally untracked files that Git should ignore.
├── pyproject.toml             # Configuration file for Python projects, including build system, dependencies, and tool settings.
├── pytest.ini                 # Configuration file for the pytest testing framework.
├── README.md                  # The main documentation file for the project.
├── setup.sh                   # A shell script for quick setup (legacy, for reference or local use).
├── models/                    # This directory stores pre-trained models used by tools like `detect` and `find`. It is typically ignored by Git due to the large file sizes.
│   ├── model_descriptions.json  # Contains descriptions of the available models.
│   ├── settings.json            # Contains settings related to model management and training runs.
│   └── *.pt                     # Pre-trained model.
├── src/                       # Contains the source code for the 🪄 ImageSorcery MCP server.
│   └── imagesorcery_mcp/       # The main package directory for the server.
│       ├── __init__.py          # Makes `imagesorcery_mcp` a Python package.
│       ├── __main__.py          # Entry point for running the package as a script.
│       ├── logging_config.py    # Configures the logging for the server.
│       ├── server.py            # The main server file, responsible for initializing FastMCP and registering tools.
│       ├── logs/                # Directory for storing server logs.
│       ├── scripts/             # Contains utility scripts for model management.
│       │   ├── README.md        # Documentation for the scripts.
│       │   ├── __init__.py      # Makes `scripts` a Python package.
│       │   ├── create_model_descriptions.py # Script to generate model descriptions.
│       │   ├── download_clip.py # Script to download CLIP models.
│       │   ├── post_install.py  # Script to run post-installation tasks.
│       │   └── download_models.py # Script to download other models (e.g., YOLO).
│       └── tools/               # Contains the implementation of individual MCP tools.
│           ├── README.md        # Documentation for the tools.
│           ├── __init__.py      # Import the central logger
│           └── *.py           # Implements the tool.
└── tests/                     # Contains test files for the project.
    ├── test_server.py         # Tests for the main server functionality.
    ├── data/                  # Contains test data, likely image files used in tests.
    └── tools/                 # Contains tests for individual tools.
```

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/sunriseapps/imagesorcery-mcp.git # Or your fork
cd imagesorcery-mcp
```

2. (Recommended) Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate # For Linux/macOS
# venv\Scripts\activate    # For Windows
```

3. Install the package in editable mode along with development dependencies:
```bash
pip install -e ".[dev]"
```
This will install `imagesorcery-mcp` and all dependencies from `[project.dependencies]` and `[project.optional-dependencies].dev` (including `build` and `twine`).

### Rules

These rules apply to all contributors: humans and AI.

0. Read all the `README.md` files in the project. Understand the project structure and purpose. Understand the guidelines for contributing. Think through how it's relate to you task, and how to make changes accordingly.
1. Read `pyproject.toml`.
Make attention to sections: `[tool.ruff]`, `[tool.ruff.lint]`, `[project.optional-dependencies]` and `[project]dependencies`.
Strictly follow code style defined in `pyproject.toml`.
Stick to the stack defined in `pyproject.toml` dependencies and do not add any new dependencies without a good reason.
2. Write your code in new and existing files.
If new dependencies needed, update `pyproject.toml` and install them via `pip install -e .` or `pip install -e ".[dev]"`. Do not install them diirectly via `pip install`.
Check out exixisting source codes for examples (e.g. `src/imagesorcery_mcp/server.py`, `src/imagesorcery_mcp/tools/crop.py`). Stick to the code style, naming conventions, input and outpput data formats, codeode structure, arcchitecture, etc. of the existing code.
3. Update related `README.md` files with your changes.
Stick to the format and structure of the existing `README.md` files.
4. Write tests for your code.
Check out existing tests for examples (e.g. `tests/test_server.py`, `tests/tools/test_crop.py`).
Stick to the code style, naming conventions, input and outpput data formats, codeode structure, arcchitecture, etc. of the existing tests.

5. Run tests and linter to ensure everything works:
```bash
pytest
ruff check .
```
In case of fails - fix the code and tests. It is **strictly required** to have all new code to comply with the linter rules and pass all tests.


### Coding hints
- Use type hints where appropriate
- Use pydantic for data validation and serialization
</details>

## 📝 Questions?

If you have any questions, issues, or suggestions regarding this project, feel free to reach out to:

- Project Author: [titulus](https://www.linkedin.com/in/titulus/) via LinkedIn
- Sunrise Apps CEO: [Vlad Karmakov](https://www.linkedin.com/in/vladkarm/) via LinkedIn

You can also open an issue in the repository for bug reports or feature requests.

## 📜 License

This project is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License.
