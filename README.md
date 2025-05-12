# ImageWizard MCP Server

An MCP server providing tools for image processing operations.

## Available Tools

**Important Note:** All file paths specified in tool arguments (e.g., `input_path`, `output_path`) must be **full paths**, not relative paths. For example, use `/home/user/images/my_image.jpg` instead of `my_image.jpg`.


- `crop` - Crops an image using OpenCV's NumPy slicing approach.
  - Required arguments:
    - `input_path` (string): Full path to the input image
    - `y_start` (integer): Starting y-coordinate (row) for the crop region (top)
    - `y_end` (integer): Ending y-coordinate (row) for the crop region (bottom)
    - `x_start` (integer): Starting x-coordinate (column) for the crop region (left)
    - `x_end` (integer): Ending x-coordinate (column) for the crop region (right)
  - Optional arguments:
    - `output_path` (string): Full path to save the output image. If not provided, will use input filename with '_cropped' suffix.
  - Returns: string (path to the cropped image)

- `resize` - Resizes an image using OpenCV.
  - Required arguments:
    - `input_path` (string): Full path to the input image
  - Optional arguments:
    - `width` (integer): Target width in pixels. If None, will be calculated based on height and preserve aspect ratio
    - `height` (integer): Target height in pixels. If None, will be calculated based on width and preserve aspect ratio
    - `scale_factor` (float): Scale factor to resize the image (e.g., 0.5 for half size, 2.0 for double size). Overrides width and height if provided
    - `interpolation` (string): Interpolation method: 'nearest', 'linear', 'area', 'cubic', 'lanczos'. Default is 'linear'
    - `output_path` (string): Full path to save the output image. If not provided, will use input filename with '_resized' suffix
  - Returns: string (path to the resized image)

- `rotate` - Rotates an image using imutils.rotate_bound function.
  - Required arguments:
    - `input_path` (string): Full path to the input image
    - `angle` (float): Angle of rotation in degrees (positive for counterclockwise)
  - Optional arguments:
    - `output_path` (string): Full path to save the output image. If not provided, will use input filename with '_rotated' suffix
  - Returns: string (path to the rotated image)

- `draw_texts` - Draws text on an image using OpenCV.
  - Required arguments:
    - `input_path` (string): Full path to the input image
    - `texts` (array): List of text items to draw. Each item should have:
      - `text` (string): The text to draw
      - `x` (integer): X-coordinate for the text position
      - `y` (integer): Y-coordinate for the text position
      - `font_scale` (float, optional): Scale factor for the font. Default is 1.0
      - `color` (array, optional): Color in BGR format [B,G,R]. Default is [0,0,0] (black)
      - `thickness` (integer, optional): Line thickness. Default is 1
      - `font_face` (string, optional): Font face to use. Default is "FONT_HERSHEY_SIMPLEX"
  - Optional arguments:
    - `output_path` (string): Full path to save the output image. If not provided, will use input filename with '_with_text' suffix
  - Returns: string (path to the image with drawn text)

- `draw_rectangles` - Draws rectangles on an image using OpenCV.
  - Required arguments:
    - `input_path` (string): Full path to the input image
    - `rectangles` (array): List of rectangle items to draw. Each item should have:
      - `x1` (integer): X-coordinate of the top-left corner
      - `y1` (integer): Y-coordinate of the top-left corner
      - `x2` (integer): X-coordinate of the bottom-right corner
      - `y2` (integer): Y-coordinate of the bottom-right corner
      - `color` (array, optional): Color in BGR format [B,G,R]. Default is [0,0,0] (black)
      - `thickness` (integer, optional): Line thickness. Default is 1
      - `filled` (boolean, optional): Whether to fill the rectangle. Default is false
  - Optional arguments:
    - `output_path` (string): Full path to save the output image. If not provided, will use input filename with '_with_rectangles' suffix
  - Returns: string (path to the image with drawn rectangles)

- `get_metainfo` - Gets metadata information about an image file.
  - Required arguments:
    - `input_path` (string): Full path to the input image
  - Returns: dictionary containing metadata about the image including:
    - filename
    - file path
    - file size (in bytes, KB, and MB)
    - dimensions (width, height, aspect ratio)
    - image format
    - color mode
    - creation and modification timestamps
    - additional image-specific information

- `detect` - Detects objects in an image using models from Ultralytics.
  - Required arguments:
    - `input_path` (string): Full path to the input image
  - Optional arguments:
    - `confidence` (float): Confidence threshold for detection (0.0 to 1.0). Default is 0.75
    - `model_name` (string): Model name to use for detection (e.g., 'yoloe-11s-seg.pt', 'yolov8m.pt'). Default is 'yoloe-11l-seg-pf.pt'
  - Returns: dictionary containing:
    - `image_path`: Path to the input image
    - `detections`: List of detected objects, each with:
      - `class`: Class name of the detected object
      - `confidence`: Confidence score (0.0 to 1.0)
      - `bbox`: Bounding box coordinates [x1, y1, x2, y2]

- `find` - Finds objects in an image based on a text description.
  - Required arguments:
    - `input_path` (string): Full path to the input image
    - `description` (string): Text description of the object to find
  - Optional arguments:
    - `confidence` (float): Confidence threshold for detection (0.0 to 1.0). Default is 0.3
    - `model_name` (string): Model name to use for finding objects (must support text prompts). Default is 'yoloe-11l-seg.pt'
    - `return_all_matches` (boolean): If True, returns all matching objects; if False, returns only the best match. Default is False
  - Returns: dictionary containing:
    - `image_path`: Path to the input image
    - `query`: The text description that was searched for
    - `found_objects`: List of found objects, each with:
      - `description`: The original search query
      - `match`: The class name of the matched object
      - `confidence`: Confidence score (0.0 to 1.0)
      - `bbox`: Bounding box coordinates [x1, y1, x2, y2]
    - `found`: Boolean indicating whether any objects were found

- `get_models` - Lists all available models in the models directory.
  - Required arguments: None
  - Returns: dictionary containing:
    - `models`: List of available models, each with:
      - `name`: Name of the model file
      - `description`: Description of the model's purpose and characteristics


## Installation

### Using repo installation

```bash
git clone https://github.com/titulus/imagewizard-mcp.git
cd imagewizard-mcp
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Quick setup

For a quick setup that installs all dependencies and downloads the YOLOv8 model:

```bash
./setup.sh
```

### Downloading models for offline use

Some tools, like `detect` and `find`, require pre-downloaded models to be available in the `models` directory in the project root. The models are not downloaded automatically when the tools are used. You need to download them explicitly:

```bash
# After installing the package
# Download models for the detect tool
download-yolo-models --ultralytics yoloe-11l-seg  # Downloads the default model
download-yolo-models --huggingface ultralytics/yolov8:yolov8m.pt

# Download models for the find tool (CLIP dependencies)
download-clip-models
```

Models will be downloaded to the `models` directory in the project root. This directory is included in `.gitignore` to prevent large model files from being committed to the repository.

#### Model Descriptions

When downloading models, the script automatically updates the `models/model_descriptions.json` file:

- For Ultralytics models: Descriptions are predefined in `src/imagewizard_mcp/scripts/create_model_descriptions.py` and include detailed information about each model's purpose, size, and characteristics.

- For Hugging Face models: Descriptions are automatically extracted from the model card on Hugging Face Hub. The script attempts to use the model name from the model index or the first line of the description.

After downloading models, it's recommended to check the descriptions in `models/model_descriptions.json` and adjust them if needed to provide more accurate or detailed information about the models' capabilities and use cases.


## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using repo installation</summary>

```json
"mcpServers": {
    "basic": {
      "command": "/path/to/imagewizard-mcp/venv/bin/python",
      "args": ["/path/to/imagewizard-mcp/src/imagewizard_mcp/server.py"],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
}
```
</details>


## Example Interactions


Call the crop tool:
```json
{
  "name": "crop",
  "arguments": {
    "input_path": "/path/to/input.png",
    "left": 10,
    "top": 20,
    "right": 100,
    "bottom": 150,
    "output_path": "/path/to/output.png"
  }
}
```

Response:
```json
{
  "result": "/path/to/output.png"
}
```

Call the resize tool:
```json
{
  "name": "resize",
  "arguments": {
    "input_path": "/path/to/input.png",
    "width": 800,
    "height": 600,
    "interpolation": "linear",
    "output_path": "/path/to/output.png"
  }
}
```

Response:
```json
{
  "result": "/path/to/output.png"
}
```

Call the rotate tool:
```json
{
  "name": "rotate",
  "arguments": {
    "input_path": "/path/to/input.png",
    "angle": 90,
    "output_path": "/path/to/output.png"
  }
}
```

Response:
```json
{
  "result": "/path/to/output.png"
}
```

Call the draw_texts tool:
```json
{
  "name": "draw_texts",
  "arguments": {
    "input_path": "/path/to/input.png",
    "texts": [
      {
        "text": "Hello World",
        "x": 50,
        "y": 50,
        "font_scale": 1.0,
        "color": [0, 0, 255],
        "thickness": 2
      },
      {
        "text": "Testing",
        "x": 100,
        "y": 150,
        "font_scale": 2.0,
        "color": [255, 0, 0],
        "thickness": 3,
        "font_face": "FONT_HERSHEY_COMPLEX"
      }
    ],
    "output_path": "/path/to/output.png"
  }
}
```

Response:
```json
{
  "result": "/path/to/output.png"
}
```

Call the draw_rectangles tool:
```json
{
  "name": "draw_rectangles",
  "arguments": {
    "input_path": "/path/to/input.png",
    "rectangles": [
      {
        "x1": 50,
        "y1": 50,
        "x2": 150,
        "y2": 100,
        "color": [0, 0, 255],
        "thickness": 2
      },
      {
        "x1": 200,
        "y1": 150,
        "x2": 300,
        "y2": 250,
        "color": [255, 0, 0],
        "thickness": 3,
        "filled": true
      }
    ],
    "output_path": "/path/to/output.png"
  }
}
```

Response:
```json
{
  "result": "/path/to/output.png"
}
```

Call the get_metainfo tool:
```json
{
  "name": "get_metainfo",
  "arguments": {
    "input_path": "/path/to/image.png"
  }
}
```

Response:
```json
{
  "result": {
    "filename": "image.png",
    "path": "/path/to/image.png",
    "size_bytes": 12345,
    "size_kb": 12.06,
    "size_mb": 0.01,
    "dimensions": {
      "width": 800,
      "height": 600,
      "aspect_ratio": 1.33
    },
    "format": "PNG",
    "color_mode": "RGB",
    "created_at": "2023-06-15T10:30:45",
    "modified_at": "2023-06-15T10:30:45",
    "additional_info": {}
  }
}
```


Call the get_models tool:
```json
{
  "name": "get_models",
  "arguments": {}
}
```

Response:
```json
{
  "result": {
    "models": [
      {
        "name": "yolov8m.pt",
        "description": "YOLOv8 Medium - Default model with good balance between accuracy and speed."
      },
      {
        "name": "yolov8n.pt",
        "description": "YOLOv8 Nano - Smallest and fastest model, suitable for edge devices with limited resources."
      }
    ]
  }
}
```

Call the detect tool:
```json
{
  "name": "detect",
  "arguments": {
    "input_path": "/path/to/input.png",
    "confidence": 0.3,
    "model_name": "yoloe-11l-seg.pt"
  }
}
```

Response:
```json
{
  "result": {
    "image_path": "/path/to/input.png",
    "detections": [
      {
        "class": "person",
        "confidence": 0.92,
        "bbox": [10.5, 20.3, 100.2, 200.1]
      },
      {
        "class": "car",
        "confidence": 0.85,
        "bbox": [150.2, 30.5, 250.1, 120.7]
      }
    ]
  }
}
```

Call the find tool:
```json
{
  "name": "find",
  "arguments": {
    "input_path": "/path/to/input.png",
    "description": "dog",
    "confidence": 0.3,
    "model_name": "yolov8s-worldv2.pt",
    "return_all_matches": true
  }
}
```

Response:
```json
{
  "result": {
    "image_path": "/path/to/input.png",
    "query": "dog",
    "found_objects": [
      {
        "description": "dog",
        "match": "dog",
        "confidence": 0.92,
        "bbox": [150.2, 30.5, 250.1, 120.7]
      },
      {
        "description": "dog",
        "match": "dog",
        "confidence": 0.85,
        "bbox": [300.5, 150.3, 400.2, 250.1]
      }
    ],
    "found": true
  }
}
```

Note: If you try to use a model that hasn't been downloaded, you'll get an error message indicating that you need to download the model first.


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
  2.0 Read `pyproject.toml`.
      Make attention to sections: `[tool.ruff]`, `[tool.ruff.lint]`, `[project.optional-dependencies]` and `[project]dependencies`.
  2.1 Write your code in new and existing files.
      If new dependencies needed, update `pyproject.toml` and install them.
  2.2 Update `README.md` with your changes.
  2.3 Write tests for your code.
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
- Register tools using `register_tool` functions within their respective modules.

### Reporting Issues

If you find a bug or have a feature request:

1. Check existing issues first
2. Create a new issue with a detailed description and steps to reproduce

### Adding New Tools

When adding new tools to the MCP server:

1. Implement the tool in the appropriate module
2. Add comprehensive tests for the new tool
3. Update documentation to include the new tool and its usage

## License

This project is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License.
