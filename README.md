# Basic MCP Server

A simple Model Context Protocol server that provides a single tool that always returns true. This is a basic boilerplate for MCP servers.

## Available Tool

- `always_true` - A tool that always returns true.
  - No required arguments

## Installation

### Using PIP

You can install `imagewizard-mcp` via pip:

```bash
pip install imagewizard-mcp
```

After installation, you can run it as a script using:

```bash
python -m imagewizard-mcp
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using repo installation</summary>

```json
"mcpServers": {
    "basic": {
      "command": "/path/to/imagewizard-mcp/venv/bin/imagewizard-mcp",
      "args": [],
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

## License

This project is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License.