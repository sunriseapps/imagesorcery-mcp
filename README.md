# Basic MCP Server

A simple Model Context Protocol server that provides a single tool that always returns true. This is a basic boilerplate for MCP servers.

## Available Tool

- `always_true` - A tool that always returns true.
  - No required arguments

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


## Example Interaction

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
  "result": true,
  "message": "This tool always returns true"
}
```

## Examples of Questions for Claude

1. "Can you use the always_true tool?"
2. "Check if the basic server is working correctly"
3. "Verify the connection to the basic MCP server"

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