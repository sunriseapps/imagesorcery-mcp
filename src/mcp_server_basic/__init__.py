from .server import serve


def main():
    """Basic MCP Server - Simple tool that always returns True"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="A basic MCP server with a simple tool"
    )

    args = parser.parse_args()
    asyncio.run(serve())


if __name__ == "__main__":
    main()