# ImageWizard MCP Server Tools Documentation

This document provides detailed information about each tool available in the ImageWizard MCP Server, including their arguments, return values, and examples of how to call them using a Claude client.

**Important Note:** All file paths specified in tool arguments (e.g., `input_path`, `output_path`) must be **full paths**, not relative paths. For example, use `/home/user/images/my_image.jpg` instead of `my_image.jpg`.

## Rules

- Register tools by defining a `register_tool` function in each tool's module. This function should accept a `FastMCP` instance and use the `@mcp.tool()` decorator to register the tool function with the server. See `src/imagewizard_mcp/server.py` for how tools are imported and registered, and individual tool files like `src/imagewizard_mcp/tools/crop.py` for examples of the `register_tool` function implementation.
- All tools should use Bounding Box format for image coordinates, e.g. `[x1, y1, x2, y2]` where `(x1, y1)` is the top-left corner and `(x2, y2)` is the bottom-right corner.


## Available Tools

### `crop`

Crops an image using OpenCV's NumPy slicing approach.

- **Required arguments:**
  - `input_path` (string): Full path to the input image
  - `x1` (integer): X-coordinate of the top-left corner
  - `y1` (integer): Y-coordinate of the top-left corner
  - `x2` (integer): X-coordinate of the bottom-right corner
  - `y2` (integer): Y-coordinate of the bottom-right corner
- **Optional arguments:**
  - `output_path` (string): Full path to save the output image. If not provided, will use input filename with '_cropped' suffix.
- **Returns:** string (path to the cropped image)

**Example Claude Request:**

```
Crop my image '/home/user/images/input.png' using bounding box [10, 10, 200, 200] and save it as '/home/user/images/cropped.png'
```

**Example Tool Call (JSON):**

```json
{
  "name": "crop",
  "arguments": {
    "input_path": "/home/user/images/input.png",
    "x1": 10,
    "y1": 10,
    "x2": 200,
    "y2": 200,
    "output_path": "/home/user/images/cropped.png"
  }
}
```

**Example Response (JSON):**

```json
{
  "result": "/home/user/images/cropped.png"
}
```

### `resize`

Resizes an image using OpenCV. The function can resize an image in three ways: by specifying both width and height, by specifying either width or height (preserving aspect ratio), or by specifying a scale factor.

- **Required arguments:**
  - `input_path` (string): Full path to the input image
- **Optional arguments:**
  - `width` (integer): Target width in pixels. If None, will be calculated based on height and preserve aspect ratio
  - `height` (integer): Target height in pixels. If None, will be calculated based on width and preserve aspect ratio
  - `scale_factor` (float): Scale factor to resize the image (e.g., 0.5 for half size, 2.0 for double size). Overrides width and height if provided
  - `interpolation` (string): Interpolation method: 'nearest', 'linear', 'area', 'cubic', 'lanczos'. Default is 'linear'
  - `output_path` (string): Full path to save the output image. If not provided, will use input filename with '_resized' suffix

- **Returns:** string (path to the resized image)

**Example Claude Request:**

```
Resize my image '/home/user/images/photo.jpg' to 800x600 pixels and save it as '/home/user/images/resized_photo.jpg'
```

**Example Tool Call (JSON):**

```json
{
  "name": "resize",
  "arguments": {
    "input_path": "/home/user/images/photo.jpg",
    "width": 800,
    "height": 600,
    "output_path": "/home/user/images/resized_photo.jpg"
  }
}
```

**Example Response (JSON):**

```json
{
  "result": "/home/user/images/resized_photo.jpg"
}
```

### `rotate`

Rotates an image using imutils.rotate_bound function. The function rotates the image by the specified angle in degrees. Positive angles represent counterclockwise rotation. The rotate_bound function ensures the entire rotated image is visible by automatically adjusting the output image size.

- **Required arguments:**
  - `input_path` (string): Full path to the input image
  - `angle` (float): Angle of rotation in degrees (positive for counterclockwise)
- **Optional arguments:**
  - `output_path` (string): Full path to save the output image. If not provided, will use input filename with '_rotated' suffix

- **Returns:** string (path to the rotated image)

**Example Claude Request:**

```
Rotate my image '/home/user/images/photo.jpg' by 45 degrees and save it as '/home/user/images/rotated_photo.jpg'
```

**Example Tool Call (JSON):**

```json
{
  "name": "rotate",
  "arguments": {
    "input_path": "/home/user/images/photo.jpg",
    "angle": 45,
    "output_path": "/home/user/images/rotated_photo.jpg"
  }
}
```

**Example Response (JSON):**

```json
{
  "result": "/home/user/images/rotated_photo.jpg"
}
```

### `draw_texts`

Draws text on an image using OpenCV. This tool allows adding multiple text elements to an image with customizable position, font, size, color, and thickness.

- **Required arguments:**
  - `input_path` (string): Full path to the input image
  - `texts` (array): List of text items to draw. Each item should have:
    - `text` (string): The text to draw
    - `x` (integer): X-coordinate for the text position
    - `y` (integer): Y-coordinate for the text position
    - `font_scale` (float, optional): Scale factor for the font. Default is 1.0
    - `color` (array, optional): Color in BGR format [B,G,R]. Default is [0,0,0] (black)
    - `thickness` (integer, optional): Line thickness. Default is 1
    - `font_face` (string, optional): Font face to use. Default is "FONT_HERSHEY_SIMPLEX". Available options: 'FONT_HERSHEY_SIMPLEX', 'FONT_HERSHEY_PLAIN', 'FONT_HERSHEY_DUPLEX', 'FONT_HERSHEY_COMPLEX', 'FONT_HERSHEY_TRIPLEX', 'FONT_HERSHEY_COMPLEX_SMALL', 'FONT_HERSHEY_SCRIPT_SIMPLEX', 'FONT_HERSHEY_SCRIPT_COMPLEX'
- **Optional arguments:**
  - `output_path` (string): Full path to save the output image. If not provided, will use input filename with '_with_text' suffix

- **Returns:** string (path to the image with drawn text)

**Example Claude Request:**

```
Add text 'Hello World' at position (50,50) and 'Copyright 2023' at the bottom right corner of my image '/home/user/images/photo.jpg'
```

**Example Tool Call (JSON):**

```json
{
  "name": "draw_texts",
  "arguments": {
    "input_path": "/home/user/images/photo.jpg",
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
        "text": "Copyright 2023",
        "x": 100,
        "y": 150,
        "font_scale": 2.0,
        "color": [255, 0, 0],
        "thickness": 3,
        "font_face": "FONT_HERSHEY_COMPLEX"
      }
    ],
    "output_path": "/home/user/images/photo_with_text.jpg"
  }
}
```

**Example Response (JSON):**

```json
{
  "result": "/home/user/images/photo_with_text.jpg"
}
```

### `draw_rectangles`

Draws rectangles on an image using OpenCV. This tool allows adding multiple rectangles to an image with customizable position, color, thickness, and fill option. Each rectangle is defined by two points: (x1, y1) for the top-left corner and (x2, y2) for the bottom-right corner.

- **Required arguments:**
  - `input_path` (string): Full path to the input image
  - `rectangles` (array): List of rectangle items to draw. Each item should have:
    - `x1` (integer): X-coordinate of the top-left corner
    - `y1` (integer): Y-coordinate of the top-left corner
    - `x2` (integer): X-coordinate of the bottom-right corner
    - `y2` (integer): Y-coordinate of the bottom-right corner
    - `color` (array, optional): Color in BGR format [B,G,R]. Default is [0,0,0] (black)
    - `thickness` (integer, optional): Line thickness. Default is 1
    - `filled` (boolean, optional): Whether to fill the rectangle. Default is false
- **Optional arguments:**
  - `output_path` (string): Full path to save the output image. If not provided, will use input filename with '_with_rectangles' suffix

- **Returns:** string (path to the image with drawn rectangles)

**Example Claude Request:**

```
Draw a red rectangle from (50,50) to (150,100) and a filled blue rectangle from (200,150) to (300,250) on my image '/home/user/images/photo.jpg'
```

**Example Tool Call (JSON):**

```json
{
  "name": "draw_rectangles",
  "arguments": {
    "input_path": "/home/user/images/photo.jpg",
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
    "output_path": "/home/user/images/photo_with_rectangles.jpg"
  }
}
```

**Example Response (JSON):**

```json
{
  "result": "/home/user/images/photo_with_rectangles.jpg"
}
```

### `get_metainfo`

Gets metadata information about an image file.

- **Required arguments:**
  - `input_path` (string): Full path to the input image
- **Returns:** dictionary containing metadata about the image including:
  - `filename`
  - `file path`
  - `file size` (in bytes, KB, and MB)
  - `dimensions` (width, height, aspect ratio)
  - `image format`
  - `color mode`
  - `creation and modification timestamps`
  - `additional image-specific information`

**Example Claude Request:**

```
Get metadata information about my image '/home/user/images/photo.jpg'
```

**Example Tool Call (JSON):**

```json
{
  "name": "get_metainfo",
  "arguments": {
    "input_path": "/home/user/images/photo.jpg"
  }
}
```

**Example Response (JSON):**

```json
{
  "result": {
    "filename": "photo.jpg",
    "path": "/home/user/images/photo.jpg",
    "size_bytes": 12345,
    "size_kb": 12.06,
    "size_mb": 0.01,
    "dimensions": {
      "width": 800,
      "height": 600,
      "aspect_ratio": 1.33
    },
    "format": "JPEG",
    "color_mode": "RGB",
    "created_at": "2023-06-15T10:30:45",
    "modified_at": "2023-06-15T10:30:45",
    "additional_info": {}
  }
}
```

### `detect`

Detects objects in an image using models from Ultralytics. This tool requires pre-downloaded models. Use the `download-yolo-models` command to download models before using this tool. If objects aren't common, consider using a specialized model.

- **Required arguments:**
  - `input_path` (string): Full path to the input image
- **Optional arguments:**
  - `confidence` (float): Confidence threshold for detection (0.0 to 1.0). Default is 0.75
  - `model_name` (string): Model name to use for detection (e.g., 'yoloe-11s-seg.pt', 'yolov8m.pt'). Default is 'yoloe-11l-seg-pf.pt'
- **Returns:** dictionary containing:
  - `image_path`: Path to the input image
  - `detections`: List of detected objects, each with:
    - `class`: Class name of the detected object
    - `confidence`: Confidence score (0.0 to 1.0)
    - `bbox`: Bounding box coordinates [x1, y1, x2, y2]

**Example Claude Request:**

```
Detect objects in my image '/home/user/images/photo.jpg' with a confidence threshold of 0.4
```

**Example Tool Call (JSON):**

```json
{
  "name": "detect",
  "arguments": {
    "input_path": "/home/user/images/photo.jpg",
    "confidence": 0.4
  }
}
```

**Example Response (JSON):**

```json
{
  "result": {
    "image_path": "/home/user/images/photo.jpg",
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

### `find`

Finds objects in an image based on a text description. This tool uses open-vocabulary detection models to find objects matching a text description. It requires pre-downloaded YOLOE models that support text prompts (e.g. yoloe-11l-seg.pt).

- **Required arguments:**
  - `input_path` (string): Full path to the input image
  - `description` (string): Text description of the object to find
- **Optional arguments:**
  - `confidence` (float): Confidence threshold for detection (0.0 to 1.0). Default is 0.3
  - `model_name` (string): Model name to use for finding objects (must support text prompts). Default is 'yoloe-11l-seg.pt'
  - `return_all_matches` (boolean): If True, returns all matching objects; if False, returns only the best match. Default is False
- **Returns:** dictionary containing:
  - `image_path`: Path to the input image
  - `query`: The text description that was searched for
  - `found_objects`: List of found objects, each with:
    - `description`: The original search query
    - `match`: The class name of the matched object
    - `confidence`: Confidence score (0.0 to 1.0)
    - `bbox`: Bounding box coordinates [x1, y1, x2, y2]
  - `found`: Boolean indicating whether any objects were found

**Example Claude Request:**

```
Find all dogs in my image '/home/user/images/photo.jpg' with a confidence threshold of 0.4
```

**Example Tool Call (JSON):**

```json
{
  "name": "find",
  "arguments": {
    "input_path": "/home/user/images/photo.jpg",
    "description": "dog",
    "confidence": 0.4,
    "return_all_matches": true
  }
}
```

**Example Response (JSON):**

```json
{
  "result": {
    "image_path": "/home/user/images/photo.jpg",
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

### `get_models`

Lists all available models in the models directory. This tool scans the models directory and returns information about all available models, including their names and descriptions.

- **Required arguments:** None
- **Returns:** dictionary containing:
  - `models`: List of available models, each with:
    - `name`: Name of the model file
    - `description`: Description of the model's purpose and characteristics

**Example Claude Request:**

```
List all available models in the models directory
```

**Example Tool Call (JSON):**

```json
{
  "name": "get_models",
  "arguments": {}
}
```

**Example Response (JSON):**

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

### `ocr`

Performs Optical Character Recognition (OCR) on an image using EasyOCR. This tool extracts text from images in various languages. The default language is English, but you can specify other languages using their language codes (e.g., 'en', 'ru', 'fr', etc.).

- **Required arguments:**
  - `input_path` (string): Full path to the input image
- **Optional arguments:**
  - `language` (string): Language code for OCR (e.g., 'en', 'ru', 'fr', etc.). Default is 'en'
- **Returns:** dictionary containing:
  - `image_path`: Path to the input image
  - `text_segments`: List of detected text segments, each with:
    - `text`: The extracted text content
    - `confidence`: Confidence score (0.0 to 1.0)
    - `bbox`: Bounding box coordinates [x1, y1, x2, y2]

**Example Claude Request:**

```
Extract text from my image '/home/user/images/document.jpg' using OCR with English language
```

**Example Tool Call (JSON):**

```json
{
  "name": "ocr",
  "arguments": {
    "input_path": "/home/user/images/document.jpg",
    "language": "en"
  }
}
```

**Example Response (JSON):**

```json
{
  "result": {
    "image_path": "/home/user/images/document.jpg",
    "text_segments": [
      {
        "text": "Hello World",
        "confidence": 0.92,
        "bbox": [10.5, 20.3, 100.2, 200.1]
      },
      {
        "text": "Copyright 2023",
        "confidence": 0.85,
        "bbox": [150.2, 30.5, 250.1, 120.7]
      }
    ]
  }
}
