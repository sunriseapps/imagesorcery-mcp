# Prompts

This directory contains reusable prompt templates for the ImageSorcery MCP server.

## Overview

Prompts provide parameterized message templates that help LLMs generate structured, purposeful responses for image processing workflows. Each prompt is designed to guide the AI through specific image manipulation tasks using the available tools.

## Architecture

- Register prompts by defining a `register_prompt` function in each prompt's module. This function should accept a `FastMCP` instance and use the `@mcp.prompt()` decorator to register the prompt function with the server. See `src/imagesorcery_mcp/server.py` for how prompts are imported and registered, and individual prompt files like `src/imagesorcery_mcp/prompts/remove_background.py` for examples of the `register_prompt` function implementation.
- When adding new prompts, ensure they are listed in alphabetical order in READMEs and in the server registration.

## Adding New Prompts

1. Create a new Python file in this directory (e.g., `new_prompt.py`)
2. Implement the prompt function with appropriate parameters and return type
3. Create a `register_prompt` function that registers the prompt with the FastMCP instance
4. Import and register the prompt in `src/imagesorcery_mcp/server.py`
5. Add documentation to this README
6. Write tests in `tests/prompts/test_new_prompt.py`

## Available Prompts

### `remove-background`

**Description:** Guides the AI through a comprehensive background removal workflow using object detection and masking tools.

**Parameters:**
- `image_path` (str): Full path to the input image
- `target_objects` (str, optional): Description of the objects to keep (default: empty for auto-detection)
- `output_path` (str, optional): Path for the final result (default: auto-generated)

**Example Usage:**
```
Use the remove-background prompt to remove the background from my photo 'portrait.jpg', keeping only the person
```

**Example Prompt Call (JSON):**
```json
{
  "name": "remove-background",
  "arguments": {
    "image_path": "/home/user/images/portrait.jpg",
    "target_objects": "person",
    "output_path": "/home/user/images/portrait_no_bg.png"
  }
}
```
