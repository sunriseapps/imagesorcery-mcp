"""
Pytest configuration file for setting up test environment.
"""

import os


def pytest_configure(config):
    """Configure pytest to set DISABLE_TELEMETRY environment variable for all tests."""
    # Set DISABLE_TELEMETRY environment variable for all tests
    os.environ['DISABLE_TELEMETRY'] = 'true'


def pytest_unconfigure(config):
    """Clean up after tests if needed."""
    # Optionally remove the environment variable after tests
    if 'DISABLE_TELEMETRY' in os.environ:
        del os.environ['DISABLE_TELEMETRY']
