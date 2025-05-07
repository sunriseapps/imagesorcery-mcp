from fastmcp import FastMCP


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def always_true() -> bool:
        """This tool always returns true."""
        return True