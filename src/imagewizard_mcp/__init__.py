from .server import serve


def main():
    """ImageWizard MCP - Image manipulation functionality for MCP"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="give a model the ability to manipulate images"
    )

    args = parser.parse_args()
    asyncio.run(serve())


if __name__ == "__main__":
    main()