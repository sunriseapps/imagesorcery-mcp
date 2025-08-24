#!/usr/bin/env python3
"""Build script to clear API keys in src/imagesorcery_mcp/telemetry_keys.py while preserving .user_id."""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telemetry keys file path
TELEMETRY_KEYS_FILE = Path('src/imagesorcery_mcp/telemetry_keys.py')

def write_empty_telemetry_keys() -> bool:
    """Overwrite telemetry_keys.py with empty API key values."""
    try:
        content = '''# Auto-generated telemetry keys module.
# This file is intended to be updated by build scripts (populate_telemetry_keys.py)
# and cleared by clear_telemetry_keys.py. Keep values as empty strings in the repo.
#
# WARNING: Do NOT commit real production keys to the repository.

AMPLITUDE_API_KEY = ""
POSTHOG_API_KEY = ""
'''
        TELEMETRY_KEYS_FILE.write_text(content)
        logger.info(f"Cleared telemetry keys in {TELEMETRY_KEYS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Failed to clear telemetry keys file: {e}")
        return False

def main():
    logger.info("Starting telemetry keys clearing process...")

    if not TELEMETRY_KEYS_FILE.exists():
        logger.warning(f"{TELEMETRY_KEYS_FILE} does not exist; creating a new cleared file.")
    if write_empty_telemetry_keys():
        logger.info("Telemetry keys cleared successfully")
        return 0
    else:
        logger.error("Failed to clear telemetry keys")
        return 1

if __name__ == '__main__':
    sys.exit(main())
