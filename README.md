# 🪄 ImageSorcery MCP
**ComputerVision-based 🪄 sorcery of image recognition and editing tools for AI assistants**

[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT) [![MCP](https://img.shields.io/badge/Protocol-MCP-lightgrey)](https://github.com/microsoft/mcp)
[![Claude](https://img.shields.io/badge/Works_with-Claude-orange)](https://claude.ai) [![Cursor](https://img.shields.io/badge/Works_with-Cursor-white)](https://cursor.so) [![Cline](https://img.shields.io/badge/Works_with-Cline-purple)](https://github.com/ClineLabs/cline)
[![Verified on MseeP](https://mseep.ai/badge.svg)](https://mseep.ai/app/2620351a-15b1-4840-a93a-cbdbd23a6944) [![PyPI Downloads](https://static.pepy.tech/badge/imagesorcery-mcp)](https://pepy.tech/projects/imagesorcery-mcp)

<a href="https://glama.ai/mcp/servers/@sunriseapps/imagesorcery-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@sunriseapps/imagesorcery-mcp/badge" />
</a>

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

> "copy photos with pets from frolder `photos` to folder `pets`"
![Copying pets](https://i.imgur.com/wsaDWbf.gif)

> "Find a cat at the photo.jpg and crop the image in a half in height and width to make the cat be centerized"
![Centerizing cat](https://i.imgur.com/tD0O3l6.gif)
😉 _**Hint:** Use full path to your files"._

> "Numerate form fields on this `form.jpg` with `foduucom/web-form-ui-field-detection` model and fill the `form.md` with a list of described fields"
![Numerate form fields](https://i.imgur.com/1SNGfaP.gif)
😉 _**Hint:** Specify the model and the confidence"._

😉 _**Hint:** Add "use imagesorcery" to make sure it will uses propper tool"._

Your tool will combine multiple tools listed below to achieve your goal.

## 🛠️ Available Tools

| Tool | Description | Example Prompt |
|------|-------------|----------------|
| `blur` | Blurs specified areas of an image using OpenCV | "Blur the area from (150, 100) to (250, 200) with a blur strength of 21 in my image 'test_image.png' and save it as 'output.png'" |
| `change_color` | Changes the color palette of an image | "Convert my image 'test_image.png' to sepia and save it as 'output.png'" |
| `crop` | Crops an image using OpenCV's NumPy slicing approach | "Crop my image 'input.png' from coordinates (10,10) to (200,200) and save it as 'cropped.png'" |
| `detect` | Detects objects in an image using models from Ultralytics | "Detect objects in my image 'photo.jpg' with a confidence threshold of 0.4" |
| `draw_arrows` | Draws arrows on an image using OpenCV | "Draw a red arrow from (50,50) to (150,100) on my image 'photo.jpg'" |
| `draw_circles` | Draws circles on an image using OpenCV | "Draw a red circle with center (100,100) and radius 50 on my image 'photo.jpg'" |
| `draw_rectangles` | Draws rectangles on an image using OpenCV | "Draw a red rectangle from (50,50) to (150,100) and a filled blue rectangle from (200,150) to (300,250) on my image 'photo.jpg'" |
| `draw_texts` | Draws text on an image using OpenCV | "Add text 'Hello World' at position (50,50) and 'Copyright 2023' at the bottom right corner of my image 'photo.jpg'" |
| `find` | Finds objects in an image based on a text description | "Find all dogs in my image 'photo.jpg' with a confidence threshold of 0.4" |
| `get_metainfo` | Gets metadata information about an image file | "Get metadata information about my image 'photo.jpg'" |
| `get_models` | Lists all available models in the models directory | "List all available models in the models directory" |
| `ocr` | Performs Optical Character Recognition (OCR) on an image using EasyOCR | "Extract text from my image 'document.jpg' using OCR with English language" |
| `overlay` | Overlays one image on top of another, handling transparency | "Overlay 'logo.png' on top of 'background.jpg' at position (10, 10)" |
| `resize` | Resizes an image using OpenCV | "Resize my image 'photo.jpg' to 800x600 pixels and save it as 'resized_photo.jpg'" |
| `rotate` | Rotates an image using imutils.rotate_bound function | "Rotate my image 'photo.jpg' by 45 degrees and save it as 'rotated_photo.jpg'" |

😉 _**Hint:** detailed information and usage instructions for each tool can be found in the tool's `/src/imagesorcery_mcp/tools/README.md`._

## 🚀 Getting Started

### Requirements

- `Python 3.10` or higher
- `ffmpeg`, `libsm6`, `libxext6`, `libgl1-mesa-glx` - system libraries required by OpenCV
- `Claude.app`, `Cline`, or another MCP client

<details>
<summary>Virtual environments (e.g. Docker)</summary>

These dependencies are typically included with OpenCV installation and don't require separate installation. But they might be missing in some virtual environments like Docker.

**For Ubuntu/Debian systems:**
```bash
sudo apt-get update && sudo apt-get install -y ffmpeg libsm6 libxext6 libgl1-mesa-glx
```

**For Docker containers:**
Add this line to your Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 libgl1-mesa-glx
```
</details>

### Installation

![ImageSorcery Demo](https://i.imgur.com/pRfTlHV.gif)
<details>
<summary>For Cline just copy-paste LLM-INSTALL.md</summary>

```md
1.  Load MCP documentation if you have the tool for it. It will give you path to *MCP-configuration file* and other needed instructions.
2.  Run command `python -m venv imagesorcery-mcp`
3.  Run command `source imagesorcery-mcp/bin/activate`
    For windows bash run command `source imagesorcery-mcp/Scripts/activate`
    For windows cmd run command `imagesorcery-mcp\Scripts\activate`
4.  Run command `pip install imagesorcery-mcp`
5.  Run command `imagesorcery-mcp --post-install`
6.  Create or modify *MCP-configuration file*.
7.  Add the `imagesorcery-mcp` server configuration to the `mcpServers` object in the *MCP-configuration file*
    `"imagesorcery-mcp": {"command": "/full/path/to/venv/bin/imagesorcery-mcp","timeout": 100}`
8.  Get available models using `get_models` tool from `imagesorcery-mcp`
9.  Attempt completion, indicating that the installation and configuration are complete.
```
</details>

1.  **Create and activate a virtual environment (Strongly Recommended):**
    For reliable installation of all components, especially the `clip` package (installed via the post-install script), it is **strongly recommended to use Python's built-in `venv` module instead of `uv venv`**.
    ```bash
    python -m venv imagesorcery-mcp
    source imagesorcery-mcp/bin/activate  # For Linux/macOS
    # source imagesorcery-mcp\Scripts\activate    # For Windows
    ```

2.  **Install the package into the activated virtual environment:**
    You can use `pip` or `uv pip`.
    ```bash
    pip install imagesorcery-mcp
    # OR, if you prefer using uv for installation into the venv:
    # uv pip install imagesorcery-mcp
    ```

3.  **Run the post-installation script:**
    This step is crucial. It downloads the required models and attempts to install the `clip` Python package from GitHub into the active virtual environment.
    ```bash
    imagesorcery-mcp --post-install
    ```

<details>
<summary>What does the post-installation script do?</summary>
The `imagesorcery-mcp --post-install` script performs the following actions:

- Creates a `models` directory (usually within the site-packages directory of your virtual environment, or a user-specific location if installed globally) to store pre-trained models.
- Generates an initial `models/model_descriptions.json` file there.
- Downloads default YOLO models (`yoloe-11l-seg-pf.pt`, `yoloe-11s-seg-pf.pt`, `yoloe-11l-seg.pt`, `yoloe-11s-seg.pt`) required by the `detect` tool into this `models` directory.
- **Attempts to install the `clip` Python package** from Ultralytics' GitHub repository directly into the active Python environment. This is required for text prompt functionality in the `find` tool.
- Downloads the CLIP model file required by the `find` tool into the `models` directory.

You can run this process anytime to restore the default models and attempt `clip` installation.
</details>

<details>
<summary>Important Notes for `uv` users (<code>uv venv</code> and <code>uvx</code>)</summary>

-   **Using `uv venv` to create virtual environments:**
    Based on testing, virtual environments created with `uv venv` may not include `pip` in a way that allows the `imagesorcery-mcp --post-install` script to automatically install the `clip` package from GitHub (it might result in a "No module named pip" error during the `clip` installation step).
    **If you choose to use `uv venv`:**
    1.  Create and activate your `uv venv`.
    2.  Install `imagesorcery-mcp`: `uv pip install imagesorcery-mcp`.
    3.  Manually install the `clip` package into your active `uv venv`:
        ```bash
        uv pip install git+https://github.com/ultralytics/CLIP.git
        ```
    3.  Run `imagesorcery-mcp --post-install`. This will download models but may fail to install the `clip` Python package.
    For a smoother automated `clip` installation via the post-install script, using `python -m venv` (as described in step 1 above) is the recommended method for creating the virtual environment.

-   **Using `uvx imagesorcery-mcp --post-install`:**
    Running the post-installation script directly with `uvx` (e.g., `uvx imagesorcery-mcp --post-install`) will likely fail to install the `clip` Python package. This is because the temporary environment created by `uvx` typically does not have `pip` available in a way the script can use. Models will be downloaded, but the `clip` package won't be installed by this command.
    If you intend to use `uvx` to run the main `imagesorcery-mcp` server and require `clip` functionality, you'll need to ensure the `clip` package is installed in an accessible Python environment that `uvx` can find, or consider installing `imagesorcery-mcp` into a persistent environment created with `python -m venv`.
</details>

## ⚙️ Configuration MCP client

Add to your MCP client these settings.
If `imagesorcery-mcp` is in your system's PATH after installation, you can use `imagesorcery-mcp` directly as the command. Otherwise, you'll need to provide the full path to the executable.

```json
"mcpServers": {
    "imagesorcery-mcp": {
      "command": "imagesorcery-mcp", // Or /full/path/to/venv/bin/imagesorcery-mcp if installed in a venv
      "transportType": "stdio",
      "autoApprove": ["blur", "change_color", "crop", "detect", "draw_arrows", "draw_circles", "draw_rectangles", "draw_texts", "find", "get_metainfo", "get_models", "ocr", "overlay", "resize", "rotate"],
      "timeout": 100
    }
}
```
<details>
<summary>If you're using the server in HTTP mode, configure your client to connect to the HTTP endpoint:</summary>

```json
"mcpServers": {
    "imagesorcery-mcp": {
      "url": "http://127.0.0.1:8000/mcp", // Use your custom host, port, and path if specified
      "transportType": "http",
      "autoApprove": ["blur", "change_color", "crop", "detect", "draw_arrows", "draw_circles", "draw_rectangles", "draw_texts", "find", "get_metainfo", "get_models", "ocr", "overlay", "resize", "rotate"],
      "timeout": 100
    }
}
```
</details>

<details>
<summary>For Windows</summary>

```json
"mcpServers": {
    "imagesorcery-mcp": {
      "command": "imagesorcery-mcp.exe", // Or C:\\full\\path\\to\\venv\\Scripts\\imagesorcery-mcp.exe if installed in a venv
      "transportType": "stdio",
      "autoApprove": ["blur", "change_color", "crop", "detect", "draw_arrows", "draw_circles", "draw_rectangles", "draw_texts", "find", "get_metainfo", "get_models", "ocr", "overlay", "resize", "rotate"],
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

### Running the Server

ImageSorcery MCP server can be run in different modes:
- `STDIO` - default
- `Streamable HTTP` - for web-based deployments
- `Server-Sent Events (SSE)` - for web-based deployments that rely on SSE

<details>
<summary>About different modes:</summary>

1. **STDIO Mode (Default)** - This is the standard mode for local MCP clients:
   ```bash
   imagesorcery-mcp
   ```

2. **Streamable HTTP Mode** - For web-based deployments:
   ```bash
   imagesorcery-mcp --transport=streamable-http
   ```
   
   With custom host, port, and path:
   ```bash
   imagesorcery-mcp --transport=streamable-http --host=0.0.0.0 --port=4200 --path=/custom-path
   ```

Available transport options:
- `--transport`: Choose between "stdio" (default), "streamable-http", or "sse"
- `--host`: Specify host for HTTP-based transports (default: 127.0.0.1)
- `--port`: Specify port for HTTP-based transports (default: 8000)
- `--path`: Specify endpoint path for HTTP-based transports (default: /mcp)
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
- Sunrise Apps CEO: [Vlad Karm](https://www.linkedin.com/in/vladkarm/) via LinkedIn

You can also open an issue in the repository for bug reports or feature requests.

## 📜 License

This project is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License.
