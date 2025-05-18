import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "imagesorcery.log")
LOG_LEVEL = logging.INFO

def setup_logging():
    """Sets up the central logger for the 🪄 ImageSorcery MCP server."""
    # Ensure the logs directory exists
    log_dir = os.path.dirname(LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)

    # Create logger
    logger = logging.getLogger("imagesorcery")
    logger.setLevel(LOG_LEVEL)

    # Prevent adding multiple handlers if setup is called more than once
    if not logger.handlers:
        # Create rotating file handler
        handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
        # Change formatter to include module name and line number
        formatter = logging.Formatter('%(asctime)s - %(name)s.%(module)s:%(lineno)d - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Optional: Add a console handler for development/debugging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(LOG_LEVEL) # Set level for console handler
        logger.addHandler(console_handler)

    print(f"Log file: {LOG_FILE}")
    return logger

# Setup logging when this module is imported
setup_logging()

# Get the logger instance to be used in other modules
logger = logging.getLogger("imagesorcery")
