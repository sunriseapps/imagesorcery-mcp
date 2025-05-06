from fastmcp import FastMCP
from pydantic import BaseModel

class Result(BaseModel):
    result: bool
    message: str

mcp = FastMCP("imagewizard-mcp")

@mcp.tool()
def always_true() -> Result:
    """A simple tool that always returns true"""
    return Result(
        result=True,
        message="This tool always returns true",
    )

if __name__ == "__main__":
    mcp.run()
