# ImageSorcery MCP Core Architecture

This directory contains the core components of the ImageSorcery MCP server, including its main entry point (`server.py`).

## `server.py`

The `server.py` file is the primary entry point for the ImageSorcery MCP server. Its main responsibilities include:

-   **Initialization of FastMCP**: It creates and configures the `FastMCP` instance, which is the foundation for the MCP server. This includes setting the server's name, instructions, and logging level.
-   **Middleware Registration**: It registers custom middleware components, such as `ImprovedValidationMiddleware` and `ErrorHandlingMiddleware`, to enhance the server's request processing and error management capabilities.
-   **Tool and Resource Registration**: It registers all available image processing tools (e.g., `blur`, `crop`, `detect`) and resources (e.g., `models`) with the `FastMCP` instance, making them accessible via the MCP protocol.
-   **Argument Parsing**: It handles command-line argument parsing for server configuration, including transport type (stdio, http), host, port, and special flags like `--post-install`.
-   **Post-Installation Tasks**: It orchestrates the execution of post-installation scripts, which are crucial for downloading necessary models and setting up the environment.
-   **Server Execution**: It starts the MCP server using the configured transport protocol.

## `middleware.py`

The `middleware.py` file defines custom middleware classes that intercept and process requests and responses within the ImageSorcery MCP server. Currently, it includes:

-   **`ImprovedValidationMiddleware`**: This middleware is designed to enhance the error messages for validation failures originating from FastMCP tools. It parses generic `ToolError` exceptions, extracts specific validation issues (e.g., unexpected or missing parameters), and transforms them into more user-friendly `McpError` messages with a standardized error code. This improves the clarity and actionability of validation errors for MCP clients.

-   **`ErrorHandlingMiddleware`**: (Note: This middleware is part of `fastmcp` but is configured and used here). This middleware provides a global mechanism for catching and handling unhandled exceptions across the server. It ensures that all errors are logged consistently, can include detailed tracebacks for debugging, and are transformed into `McpError` objects, providing a standardized error response format for clients.
