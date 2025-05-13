from .logging_config import logger
from .server import mcp


def main():
    logger.info("ImageWizard MCP server main function started")
    mcp.run()


if __name__ == "__main__":
    main()
