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

## How It Works

### 1. Configuration File Creation
- During installation (`imagesorcery-mcp --post-install`), a `config.toml` file is created in the root directory
- The file is created from `config.default` template in the repository
- If the template is missing, a basic config file with default values is created

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

## File Structure

```
project_root/
├── config.default          # Template configuration file (in repository)
├── config.toml             # User configuration file (created during install)
├── src/imagesorcery_mcp/
│   ├── config.py           # Configuration management system
│   └── tools/
│       ├── config.py       # MCP config tool
│       ├── detect.py       # Updated to use config defaults
│       ├── find.py         # Updated to use config defaults
│       ├── blur.py         # Updated to use config defaults
│       ├── ocr.py          # Updated to use config defaults
│       ├── resize.py       # Updated to use config defaults
│       └── draw_text.py    # Updated to use config defaults
└── test_config.py          # Test script for configuration system
```

## Configuration File Format

The `config.toml` file uses TOML format:

```toml
# ImageSorcery MCP Configuration

[detection]
confidence_threshold = 0.75
default_model = "yoloe-11l-seg-pf.pt"

[find]
confidence_threshold = 0.75
default_model = "yoloe-11l-seg-pf.pt"

[blur]
strength = 15

[text]
font_scale = 1.0

[drawing]
color = [0, 0, 0]
thickness = 1

[ocr]
language = "en"

[resize]
interpolation = "linear"
```

## Key Features

### 1. Validation
- All configuration values are validated using Pydantic
- Confidence thresholds must be between 0.0 and 1.0
- Blur strength must be an odd number
- Color values must be 0-255
- Interpolation methods are restricted to valid options

### 2. Runtime vs Persistent Changes
- Runtime changes: Apply only to current session
- Persistent changes: Saved to `config.toml` file
- Runtime changes can be reset without affecting persistent settings

### 3. Backward Compatibility
- Tools work exactly as before when parameters are explicitly provided
- Configuration only provides defaults when parameters are omitted
- No breaking changes to existing tool interfaces

### 4. Error Handling
- Graceful fallback to hardcoded defaults if config file is corrupted
- Clear error messages for invalid configuration values
- Automatic config file creation if missing

## Installation Integration

The configuration system is integrated into the post-installation process:

1. `imagesorcery-mcp --post-install` creates `config.toml`
2. Config file is created from `config.default` template
3. If template is missing, creates basic config with defaults
4. User can immediately start using the config tool

## Testing

A comprehensive test suite (`test_config.py`) verifies:
- Configuration file creation
- Default value loading
- Runtime updates
- Persistent updates
- Validation
- Reset functionality

Run tests with: `python test_config.py`

## Benefits

1. **User-Friendly**: No CLI needed, everything accessible through MCP
2. **Flexible**: Runtime and persistent configuration options
3. **Safe**: Comprehensive validation prevents invalid configurations
4. **Backward Compatible**: Existing workflows continue to work
5. **Discoverable**: Config tool is available through MCP interface
6. **Maintainable**: Clean separation between config and tool logic
