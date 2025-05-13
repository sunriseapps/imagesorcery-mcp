# ImageWizard MCP Server

An MCP server providing tools for image processing operations.

## Available Tools

_**Note:** detailed information and usage instructions for each tool can be found in the tool's `/src/imagewizard_mcp/tools/README.md`._

- `crop`: Crops an image using OpenCV's NumPy slicing approach.
- `resize`: Resizes an image using OpenCV.
- `rotate`: Rotates an image using imutils.rotate_bound function.
- `draw_texts`: Draws text on an image using OpenCV.
- `draw_rectangles`: Draws rectangles on an image using OpenCV.
- `get_metainfo`: Gets metadata information about an image file.
- `detect`: Detects objects in an image using models from Ultralytics.
- `find`: Finds objects in an image based on a text description.
- `get_models`: Lists all available models in the models directory.
- `ocr`: Performs Optical Character Recognition (OCR) on an image using EasyOCR. _(Might be slow on first use.)_

## Examples of Questions for Claude

1. "Crop my image 'input.png' from coordinates (10,10) to (200,200) and save it as 'cropped.png'"
2. "Get metadata information about my image 'photo.jpg'"
3. "Resize my image 'photo.jpg' to 800x600 pixels and save it as 'resized_photo.jpg'"
4. "Rotate my image 'photo.jpg' by 45 degrees and save it as 'rotated_photo.jpg'"
5. "Detect objects in my image 'photo.jpg' with a confidence threshold of 0.4"
6. "List all available models in the models directory"
7. "Add text 'Hello World' at position (50,50) and 'Copyright 2023' at the bottom right corner of my image 'photo.jpg'"
8. "Draw a red rectangle from (50,50) to (150,100) and a filled blue rectangle from (200,150) to (300,250) on my image 'photo.jpg'"
9. "Find all dogs in my image 'photo.jpg' with a confidence threshold of 0.4"
10. "Extract text from my image 'document.jpg' using OCR with English language"


## Installation

```bash
git clone https://github.com/titulus/imagewizard-mcp.git
cd imagewizard-mcp
./setup.sh
```

The `setup.sh` script performs the following actions:
- Creates a Python virtual environment named `venv` if it doesn't already exist.
- Activates the virtual environment.
- Installs the project's core dependencies using `pip install -e .`.
- Creates a `models` directory to store pre-trained models.
- Runs the `create-model-descriptions` script to generate the initial `models/model_descriptions.json` file.
- Downloads default YOLO models (`yoloe-11l-seg-pf.pt`, `yoloe-11s-seg-pf.pt`, `yoloe-11l-seg.pt`, `yoloe-11s-seg.pt`) required by the `detect` tool.
- Downloads CLIP models required by the `find` tool for text prompts.

After running `setup.sh`, you will have a virtual environment set up, project dependencies installed, and necessary default models downloaded.

## Configuration MCP client

Add to your **Claude.app** or **Cline** or other MCP client these settings:

### Linux configuration

```json
"mcpServers": {
    "imagewizard-mcp": {
      "command": "/path/to/imagewizard-mcp/venv/bin/imagewizard-mcp",
      "args": [],
      "env": {},
      "disabled": false,
      "autoApprove": [
        "detect",
        "crop",
        "get_models",
        "draw_texts",
        "get_metainfo",
        "rotate",
        "resize",
        "classify",
        "draw_rectangles",
        "find",
        "ocr"
      ],
      "timeout": 60,
      "transportType": "stdio"
    }
}
```

### Windows configuration

```json
"mcpServers": {
    "imagewizard-mcp": {
      "command": "C:\\path\\to\\imagewizard-mcp\\venv\\Scripts\\imagewizard-mcp.exe",
      "args": [],
      "disabled": false,
      "autoApprove": [
        "detect",
        "crop",
        "get_models",
        "draw_texts",
        "get_metainfo",
        "rotate",
        "resize",
        "classify",
        "draw_rectangles",
        "find",
        "ocr"
      ],
      "timeout": 60
    }
}
```


## Downloading extra models

Some tools, like `detect` and `find`, for specific cases require pre-downloaded models to be available in the `models` directory in the project root. The models are not downloaded automatically when the tools are used. You need to download them explicitly:

```bash
# Download models for the detect tool
download-yolo-models --ultralytics yoloe-11l-seg
download-yolo-models --huggingface ultralytics/yolov8:yolov8m.pt
```

Models will be downloaded to the `models` directory in the project root. This directory is included in `.gitignore` to prevent large model files from being committed to the repository.

### Model Descriptions

When downloading models, the script automatically updates the `models/model_descriptions.json` file:

- For Ultralytics models: Descriptions are predefined in `src/imagewizard_mcp/scripts/create_model_descriptions.py` and include detailed information about each model's purpose, size, and characteristics.

- For Hugging Face models: Descriptions are automatically extracted from the model card on Hugging Face Hub. The script attempts to use the model name from the model index or the first line of the description.

After downloading models, it's recommended to check the descriptions in `models/model_descriptions.json` and adjust them if needed to provide more accurate or detailed information about the models' capabilities and use cases.


## Directory Structure

This repository is organized as follows:

```
.
├── .gitignore                 # Specifies intentionally untracked files that Git should ignore.
├── pyproject.toml             # Configuration file for Python projects, including build system, dependencies, and tool settings.
├── pytest.ini                 # Configuration file for the pytest testing framework.
├── README.md                  # The main documentation file for the project.
├── setup.sh                   # A shell script for quick setup.
├── models/                    # This directory stores pre-trained models used by tools like `detect` and `find`. It is typically ignored by Git due to the large file sizes.
│   ├── model_descriptions.json  # Contains descriptions of the available models.
│   ├── settings.json            # Contains settings related to model management and training runs.
│   └── *.pt                     # Pre-trained model.
├── src/                       # Contains the source code for the ImageWizard MCP server.
│   └── imagewizard_mcp/       # The main package directory for the server.
│       ├── __init__.py          # Makes `imagewizard_mcp` a Python package.
│       ├── __main__.py          # Entry point for running the package as a script.
│       ├── logging_config.py    # Configures the logging for the server.
│       ├── server.py            # The main server file, responsible for initializing FastMCP and registering tools.
│       ├── logs/                # Directory for storing server logs.
│       ├── scripts/             # Contains utility scripts for model management.
│       │   ├── __init__.py      # Makes `scripts` a Python package.
│       │   ├── create_model_descriptions.py # Script to generate model descriptions.
│       │   ├── download_clip.py # Script to download CLIP models.
│       │   └── download_models.py # Script to download other models (e.g., YOLO).
│       └── tools/               # Contains the implementation of individual MCP tools.
│           ├── __init__.py      # Makes `tools` a Python package and imports/registers the individual tools.
│           ├── README.md        # Documentation for the tools.
│           └── *.py           # Implements the tool.
└── tests/                     # Contains test files for the project.
    ├── test_server.py         # Tests for the main server functionality.
    ├── data/                  # Contains test data, likely image files used in tests.
    └── tools/                 # Contains tests for individual tools.

```

## Contributing

We welcome contributions to imagewizard-mcp! Here's how you can help:

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/titulus/imagewizard-mcp.git
```

2. Create and activate a virtual environment:
```bash
cd imagewizard-mcp
python -m venv venv
```

On Windows:
```bash
venv\Scripts\activate
```

On macOS/Linux:
```bash
source venv/bin/activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Code Quality

#### Linting with Ruff

We use Ruff for linting our codebase. To run the linter:

```bash
ruff check .
```

To automatically fix issues that can be fixed:

```bash
ruff check --fix .
```

To format your code with Ruff:

```bash
ruff format .
```

### Making Changes

1. Create a new branch for your feature:
```bash
git checkout -b feature-name
```

2. Make your changes.
  - Read `pyproject.toml`.
    Make attention to sections: `[tool.ruff]`, `[tool.ruff.lint]`, `[project.optional-dependencies]` and `[project]dependencies`.
  - Write your code in new and existing files.
    If new dependencies needed, update `pyproject.toml` and install them.
  - Update related `README.md` files with your changes.
  - Write tests for your code.
    See existing tests for examples (e.g. `tests/tools/test_crop.py`).

3. Run tests and linter to ensure everything works:
```bash
pytest
ruff check .
```
If it fails - fix the code and tests. It is strictly required to have all new code to comply with the code style and pass all tests.

### Submitting Changes

1. Push your changes to your fork:
```bash
git push origin feature-name
```

2. Create a pull request with a description of your changes

### Code Style

- Follow PEP 8 style guidelines (enforced by Ruff)
- Use type hints where appropriate
- Use pydantic for data validation and serialization

### Reporting Issues

If you find a bug or have a feature request:

1. Check existing issues first
2. Create a new issue with a detailed description and steps to reproduce


## License

This project is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License.
