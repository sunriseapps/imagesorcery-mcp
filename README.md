# ImageWizard MCP Server

An MCP server providing tools for image processing operations.

## Available Tools


- `crop` - Crops an image using OpenCV's NumPy slicing approach.
  - Required arguments:
    - `input_path` (string): Path to the input image
    - `y_start` (integer): Starting y-coordinate (row) for the crop region (top)
    - `y_end` (integer): Ending y-coordinate (row) for the crop region (bottom)
    - `x_start` (integer): Starting x-coordinate (column) for the crop region (left)
    - `x_end` (integer): Ending x-coordinate (column) for the crop region (right)
  - Optional arguments:
    - `output_path` (string): Path to save the output image. If not provided, will use input filename with '_cropped' suffix.
  - Returns: string (path to the cropped image)

- `resize` - Resizes an image using OpenCV.
  - Required arguments:
    - `input_path` (string): Path to the input image
  - Optional arguments:
    - `width` (integer): Target width in pixels. If None, will be calculated based on height and preserve aspect ratio
    - `height` (integer): Target height in pixels. If None, will be calculated based on width and preserve aspect ratio
    - `scale_factor` (float): Scale factor to resize the image (e.g., 0.5 for half size, 2.0 for double size). Overrides width and height if provided
    - `interpolation` (string): Interpolation method: 'nearest', 'linear', 'area', 'cubic', 'lanczos'. Default is 'linear'
    - `output_path` (string): Path to save the output image. If not provided, will use input filename with '_resized' suffix
  - Returns: string (path to the resized image)

- `rotate` - Rotates an image using imutils.rotate_bound function.
  - Required arguments:
    - `input_path` (string): Path to the input image
    - `angle` (float): Angle of rotation in degrees (positive for counterclockwise)
  - Optional arguments:
    - `output_path` (string): Path to save the output image. If not provided, will use input filename with '_rotated' suffix
  - Returns: string (path to the rotated image)

- `get_metainfo` - Gets metadata information about an image file.
  - Required arguments:
    - `input_path` (string): Path to the input image
  - Returns: dictionary containing metadata about the image including:
    - filename
    - file path
    - file size (in bytes, KB, and MB)
    - dimensions (width, height, aspect ratio)
    - image format
    - color mode
    - creation and modification timestamps
    - additional image-specific information

- `detect` - Detects objects in an image using YOLOv8 from Ultralytics.
  - Required arguments:
    - `input_path` (string): Path to the input image
  - Optional arguments:
    - `confidence` (float): Confidence threshold for detection (0.0 to 1.0). Default is 0.25
    - `model_size` (string): YOLOv8 model size: 'n', 's', 'm', 'l', or 'x'. Default is 'm'
  - Returns: dictionary containing:
    - `image_path`: Path to the input image
    - `detections`: List of detected objects, each with:
      - `class`: Class name of the detected object
      - `confidence`: Confidence score (0.0 to 1.0)
      - `bbox`: Bounding box coordinates [x1, y1, x2, y2]


## Installation

### Using repo installation

```bash
git clone https://github.com/titulus/imagewizard-mcp.git
cd imagewizard-mcp
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Downloading YOLOv8 models for offline use

The `detect` tool requires YOLOv8 models, which are downloaded automatically when the tool is first used. However, if you plan to use the tool in an offline environment, you should download the models during installation:

```bash
# After installing the package
download-yolo-models --model-size m  # Downloads the medium-sized model (default)

# Or download all available models
download-yolo-models --all  # Downloads all model sizes (n, s, m, l, x)
```

This ensures the models are available locally when you need to use the `detect` tool without internet access.

### Quick setup

For a quick setup that installs all dependencies and downloads the YOLOv8 model:

```bash
./setup.sh
```

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

Call the detect tool:
```json
{
  "name": "detect",
  "arguments": {
    "input_path": "/path/to/input.png",
    "confidence": 0.3,
    "model_size": "m"
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


## Examples of Questions for Claude

1. "Crop my image 'input.png' from coordinates (10,10) to (200,200) and save it as 'cropped.png'"
2. "Get metadata information about my image 'photo.jpg'"
3. "Resize my image 'photo.jpg' to 800x600 pixels and save it as 'resized_photo.jpg'"
4. "Rotate my image 'photo.jpg' by 45 degrees and save it as 'rotated_photo.jpg'"
5. "Detect objects in my image 'photo.jpg' with a confidence threshold of 0.4"

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