1.  Load MCP documentation if you have the tool for it. It will give you path to *MCP-configuration file* and other needed instructions.
2.  Run command `python -m venv imagesorcery-mcp`
3.  Run command `source imagesorcery-mcp/bin/activate`
    For windows bash run command `source imagesorcery-mcp/Scripts/activate`
    For windows cmd run command `imagesorcery-mcp\Scripts\activate`
4.  Run command `pip install imagesorcery-mcp`
5.  Run command `imagesorcery-mcp --post-install`
6.  Create or modify *MCP-configuration file*.
7.  Add the `imagesorcery-mcp` server configuration to the `mcpServers` object in the *MCP-configuration file*
    `"imagesorcery-mcp": {"command": "/full/path/to/venv/bin/imagesorcery-mcp","timeout": 100}`
8.  Get available models using `get_models` tool from `imagesorcery-mcp`
9.  Attempt completion, indicating that the installation and configuration are complete.