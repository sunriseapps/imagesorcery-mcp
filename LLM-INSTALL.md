1.  Load MCP documentation if you have the tool for it. It will give you path to *MCP-configuration file* and other needed instructions.
2.  Run command `pipx install imagesorcery-mcp`
3.  Run command `imagesorcery-mcp --post-install`
4.  Create or modify *MCP-configuration file*.
5.  Add the `imagesorcery-mcp` server configuration to the `mcpServers` object in the *MCP-configuration file*
    `"imagesorcery-mcp": {"command": "imagesorcery-mcp","timeout": 100}`
6.  Access available models using `models://list` resource from `imagesorcery-mcp`
7.  Attempt completion, indicating that the installation and configuration are complete.