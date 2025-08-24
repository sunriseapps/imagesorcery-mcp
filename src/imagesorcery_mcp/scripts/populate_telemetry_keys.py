#!/usr/bin/env python3
"""Build script to populate src/imagesorcery_mcp/telemetry_keys.py with API keys from environment variables or .env file."""

import logging
import os
import sys
from pathlib import Path
from typing import Dict

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telemetry keys file path
TELEMETRY_KEYS_FILE = Path('src/imagesorcery_mcp/telemetry_keys.py')

def get_telemetry_keys() -> Dict[str, str]:
    """Get telemetry API keys from environment variables and .env file.

    Priority order:
    1. Environment variables
    2. .env file

    Returns:
        Dictionary containing telemetry API keys
    """
    keys = {}

    # Load .env file if available
    if DOTENV_AVAILABLE:
        env_file = Path('.env')
        if env_file.exists():
            load_dotenv(env_file)
            logger.debug("Loaded .env file")

    # Get Amplitude API key (env var takes priority)
    amplitude_key = os.environ.get('IMAGESORCERY_AMPLITUDE_API_KEY', '')
    keys['AMPLITUDE_API_KEY'] = amplitude_key
    if amplitude_key:
        logger.debug("Found IMAGESORCERY_AMPLITUDE_API_KEY")

    # Get PostHog API key (env var takes priority)
    posthog_key = os.environ.get('IMAGESORCERY_POSTHOG_API_KEY', '')
    keys['POSTHOG_API_KEY'] = posthog_key
    if posthog_key:
        logger.debug("Found IMAGESORCERY_POSTHOG_API_KEY")

    return keys

def write_telemetry_keys_file(keys: Dict[str, str]) -> bool:
    """Write the telemetry_keys.py file with provided keys.

    Args:
        keys: Dict with 'AMPLITUDE_API_KEY' and 'POSTHOG_API_KEY'

    Returns:
        True if successful, False otherwise
    """
    try:
        content = f'''# Auto-generated telemetry keys module.
# This file is intended to be updated by build scripts (populate_telemetry_keys.py)
# and cleared by clear_telemetry_keys.py. Keep values as empty strings in the repo.
#
# WARNING: Do NOT commit real production keys to the repository.

AMPLITUDE_API_KEY = "{keys.get("AMPLITUDE_API_KEY", "")}"
POSTHOG_API_KEY = "{keys.get("POSTHOG_API_KEY", "")}"
'''
        TELEMETRY_KEYS_FILE.write_text(content)
        logger.info(f"Wrote telemetry keys to {TELEMETRY_KEYS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Failed to write telemetry keys file: {e}")
        return False

def main():
    """Main entry point to populate telemetry_keys.py."""
    logger.info("Starting telemetry keys population process...")

    # Optionally skip
    if os.environ.get('SKIP_TELEMETRY_POPULATION', '').lower() in ('true', '1', 'yes'):
        logger.info("Telemetry population skipped via SKIP_TELEMETRY_POPULATION environment variable")
        return 0

    keys = get_telemetry_keys()

    found_keys = [k for k, v in keys.items() if v]
    empty_keys = [k for k, v in keys.items() if not v]

    if found_keys:
        logger.info(f"Found telemetry keys: {', '.join(found_keys)}")
    if empty_keys:
        logger.info(f"Empty telemetry keys (will remain empty): {', '.join(empty_keys)}")

    if write_telemetry_keys_file(keys):
        logger.info("Telemetry keys population completed successfully")
        return 0
    else:
        logger.error("Telemetry keys population failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
