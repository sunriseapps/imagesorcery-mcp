import os
import subprocess
import sys

# Import the central logger
from .logging_config import logger

logger.info("🪄 ImageSorcery MCP server __main__ executed")

# Get the directory of the current script (__main__.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to server.py
server_script_path = os.path.join(script_dir, "server.py")

logger.info(f"Executing server script: {server_script_path}")
# Execute server.py as a subprocess
# This ensures the __name__ == "__main__" block in server.py is executed
subprocess.run([sys.executable, server_script_path])
logger.info("Server script execution finished")
