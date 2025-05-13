import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "imagewizard.log")
LOG_LEVEL = logging.INFO

def setup_logging():
    """Sets up the central logger for the ImageWizard MCP server."""
    # Ensure the logs directory exists
    log_dir = os.path.dirname(LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)

    # Create logger
    logger = logging.getLogger("imagewizard")
    logger.setLevel(LOG_LEVEL)

    # Prevent adding multiple handlers if setup is called more than once
    if not logger.handlers:
        # Create rotating file handler
        handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Optional: Add a console handler for development/debugging
        # console_handler = logging.StreamHandler()
        # console_handler.setFormatter(formatter)
        # logger.addHandler(console_handler)

    return logger

# Setup logging when this module is imported
setup_logging()

# Get the logger instance to be used in other modules
logger = logging.getLogger("imagewizard")
