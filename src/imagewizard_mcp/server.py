from fastmcp import FastMCP
from imagewizard_mcp.tools.always_true import always_true as always_true_impl

mcp = FastMCP("imagewizard-mcp")

@mcp.tool()
def always_true() -> bool:
    return always_true_impl()

if __name__ == "__main__":
    mcp.run()
