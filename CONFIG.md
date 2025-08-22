# ImageSorcery MCP Configuration System

## What Can Be Configured

The configuration system covers the following parameters:

### Detection Tool
- `detection.confidence_threshold` (0.0-1.0): Default confidence threshold for object detection
- `detection.default_model`: Default model for detection tool

### Find Tool  
- `find.confidence_threshold` (0.0-1.0): Default confidence threshold for object finding
- `find.default_model`: Default model for find tool (can be different from detection)

### Blur Tool
- `blur.strength` (odd number): Default blur strength

### Text Drawing
- `text.font_scale` (>0.0): Default font scale for text drawing

### Drawing Operations
- `drawing.color` [B,G,R]: Default color in BGR format (0-255 each)
- `drawing.thickness` (≥1): Default line thickness

### OCR Tool
- `ocr.language`: Default language code (e.g., "en", "fr", "ru")

### Resize Tool
- `resize.interpolation`: Default interpolation method ("nearest", "linear", "area", "cubic", "lanczos")

### Telemetry
- `telemetry.enabled` (true/false): Enable or disable anonymous, non-invasive telemetry to help improve the project. Defaults to `false`.

## How It Works

### 1. Configuration File Creation
- During installation (`imagesorcery-mcp --post-install`), a `config.toml` file is created in the root directory with default values.

### 2. Configuration Loading
- The system automatically loads configuration from `config.toml` on startup
- If no config file exists, it creates one with default values
- Configuration is validated using Pydantic models

### 3. Tool Integration
- Tools now check for configuration defaults when parameters are not provided
- For example: `detect(input_path="image.jpg")` will use `config.detection.confidence_threshold` and `config.detection.default_model`
- Explicit parameters still override config defaults

### 4. MCP Config Tool
- A new `config` tool is available through the MCP interface
- Allows viewing and updating configuration values
- Supports both runtime (session-only) and persistent changes

## Usage Examples

### View Current Configuration
```python
# Get entire configuration
config(action="get")

# Get specific value
config(action="get", key="detection.confidence_threshold")
```

### Update Configuration
```python
# Runtime change (current session only)
config(action="set", key="detection.confidence_threshold", value=0.8)

# Persistent change (saved to file)
config(action="set", key="blur.strength", value=21, persist=True)

# Update multiple values
config(action="set", key="drawing.color", value=[255, 0, 0])  # Red color
```

### Reset Runtime Changes
```python
# Reset all runtime overrides
config(action="reset")
```
