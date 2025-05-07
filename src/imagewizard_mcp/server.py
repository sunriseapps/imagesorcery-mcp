from fastmcp import FastMCP
from imagewizard_mcp.tools.always_true import register_tool as register_always_true_tool
from imagewizard_mcp.tools.echo import register_tool as register_echo_tool

mcp = FastMCP("imagewizard-mcp")

register_always_true_tool(mcp)
register_echo_tool(mcp)

if __name__ == "__main__":
    mcp.run()
