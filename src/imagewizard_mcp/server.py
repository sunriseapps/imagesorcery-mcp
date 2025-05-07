from fastmcp import FastMCP
from imagewizard_mcp.tools.always_true import register_tool as register_always_true_tool
from imagewizard_mcp.tools.echo import register_tool as register_echo_tool
from imagewizard_mcp.tools.crop import register_tool as register_crop_tool
from imagewizard_mcp.tools.resize import register_tool as register_resize_tool
from imagewizard_mcp.tools import metainfo

mcp = FastMCP(
    name="imagewizard-mcp",
    instructions="A simple MCP server."
)

register_always_true_tool(mcp)
register_echo_tool(mcp)
register_crop_tool(mcp)
register_resize_tool(mcp)
metainfo.register_tool(mcp)

if __name__ == "__main__":
    mcp.run()
