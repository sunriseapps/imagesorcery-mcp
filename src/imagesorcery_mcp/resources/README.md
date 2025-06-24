# 🪄 ImageSorcery MCP Server Resources Documentation

This document provides detailed information about each resource available in the 🪄 ImageSorcery MCP Server, including their URIs, descriptions, and examples of how to access them using a Claude client.

## Rules

These rules apply to all contributors: humans and AI.

- Register resources by defining a `register_resource` function in each resource's module. This function should accept a `FastMCP` instance and use the `@mcp.resource()` decorator to register the resource function with the server. See `src/imagesorcery_mcp/server.py` for how resources are imported and registered, and individual resource files like `src/imagesorcery_mcp/resources/models.py` for examples of the `register_resource` function implementation.
- When adding new resources, ensure they are listed in alphabetical order in READMEs and in the server registration.


## Available Resources

### `models://list`

Lists all available models in the models directory. This resource scans the models directory and returns information about all available models, including their names, descriptions, and file paths.

- **URI:** `models://list`
- **Returns:** JSON string containing:
  - `models`: List of available models, each with:
    - `name`: Name of the model file (relative path from the models directory)
    - `description`: Description of the model's purpose and characteristics
    - `path`: Full path to the model file

**Example Claude Request:**

```
List all available models in the models directory
```

**Example Resource Access (JSON):**

```json
{
  "resource": "models://list"
}
```

**Example Response (JSON):**

```json
{
  "models": [
    {
      "name": "yolov8m.pt",
      "description": "YOLOv8 Medium - Default model with good balance between accuracy and speed.",
      "path": "/path/to/models/yolov8m.pt"
    },
    {
      "name": "yolov8n.pt",
      "description": "YOLOv8 Nano - Smallest and fastest model, suitable for edge devices with limited resources.",
      "path": "/path/to/models/yolov8n.pt"
    }
  ]
}