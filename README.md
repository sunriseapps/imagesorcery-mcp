# Basic MCP Server

A simple Model Context Protocol server that provides tools for basic operations. This is a basic boilerplate for MCP servers.

## Available Tools

- `always_true` - This tool always returns true.
  - No required arguments
  - Returns: boolean (always true)

- `echo` - Echoes the input text.
  - Required arguments: `text` (string) - The text to echo
  - Returns: string (the same text that was provided)

- `crop` - Crops an image based on provided coordinates..
  - Required arguments:
    - `input_path` (string): Path to the input image
    - `left` (integer): Left coordinate of crop box
    - `top` (integer): Top coordinate of crop box
    - `right` (integer): Right coordinate of crop box
    - `bottom` (integer): Bottom coordinate of crop box
  - Optional arguments:
    - `output_path` (string): Path to save the output image. If not provided, will use input filename with '_cropped' suffix.
  - Returns: string (path to the cropped image)

## Installation

### Using repo installation

```bash
git clone https://github.com/titulus/imagewizard-mcp.git
cd imagewizard-mcp
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
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

Call the always_true tool:
```json
{
  "name": "always_true",
  "arguments": {}
}
```

Response:
```json
{
  "result": true
}
```

Call the echo tool:
```json
{
  "name": "echo",
  "arguments": {
    "text": "Hello, world!"
  }
}
```

Response:
```json
{
  "result": "Hello, world!"
}
```

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

## Examples of Questions for Claude

1. "Can you use the always_true tool?"
2. "Check if the basic server is working correctly"
3. "Verify the connection to the basic MCP server"
4. "Echo back the text 'Hello from MCP server'"
5. "Crop my image 'input.png' from coordinates (10,10) to (200,200) and save it as 'cropped.png'"

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

### Making Changes

1. Create a new branch for your feature:
```bash
git checkout -b feature-name
```

2. Make your changes
  2.1 Write your code
  2.2 Update README.md with your changes
  2.3 Write tests for your code

3. Run tests to ensure everything works:
```bash
pytest
```
If it's not - fix the code and tests. It is strictly required to have all new code be covered with documentation and tests and all tests passing.

### Submitting Changes

1. Push your changes to your fork:
```bash
git push origin feature-name
```

2. Create a pull request with a description of your changes

### Code Style

- Follow PEP 8 style guidelines
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