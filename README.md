# 🪄 ImageSorcery MCP Server

An MCP server providing tools for image processing operations.

## Available Tools

_**Note:** detailed information and usage instructions for each tool can be found in the tool's `/src/imagesorcery_mcp/tools/README.md`._

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
git clone https://github.com/titulus/imagesorcery-mcp.git
cd imagesorcery-mcp
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
    "imagesorcery-mcp": {
      "command": "/path/to/imagesorcery-mcp/venv/bin/imagesorcery-mcp",
      "transportType": "stdio",
      "autoApprove": ["detect", "crop", "get_models", "draw_texts", "get_metainfo", "rotate", "resize", "classify", "draw_rectangles", "find", "ocr"],
      "timeout": 100
    }
}
```

### Windows configuration

```json
"mcpServers": {
    "imagesorcery-mcp": {
      "command": "C:\\path\\to\\imagesorcery-mcp\\venv\\Scripts\\imagesorcery-mcp.exe",
      "transportType": "stdio",
      "autoApprove": ["detect", "crop", "get_models", "draw_texts", "get_metainfo", "rotate", "resize", "classify", "draw_rectangles", "find", "ocr"],
      "timeout": 100
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

- For Ultralytics models: Descriptions are predefined in `src/imagesorcery_mcp/scripts/create_model_descriptions.py` and include detailed information about each model's purpose, size, and characteristics.

- For Hugging Face models: Descriptions are automatically extracted from the model card on Hugging Face Hub. The script attempts to use the model name from the model index or the first line of the description.

After downloading models, it's recommended to check the descriptions in `models/model_descriptions.json` and adjust them if needed to provide more accurate or detailed information about the models' capabilities and use cases.

<details>
<summary>Contributing</summary>

## Contributing

### Directory Structure

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
git clone https://github.com/titulus/imagesorcery-mcp.git
cd imagesorcery-mcp
```

2. Perform Client's install described above.
```bash
./setup.sh
```

3. Activate a virtual environment:
```bash
venv\Scripts\activate # win
source venv/bin/activate # mac/linux
```

4. Install development dependencies:
```bash
pip install -e ".[dev]"
```

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

## Questions?

If you have any questions, issues, or suggestions regarding this project, feel free to reach out to:

- Project Author: [titulus](https://www.linkedin.com/in/titulus/) via LinkedIn
- Sunrise Apps CEO: [Vlad Karmakov](https://www.linkedin.com/in/vladkarm/) via LinkedIn

You can also open an issue in the repository for bug reports or feature requests.


## License

This project is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License.
