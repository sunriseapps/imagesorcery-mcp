"""
Tests for the telemetry system.
"""

import logging
import os
import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

from imagesorcery_mcp.config import get_config_manager
from imagesorcery_mcp.logging_config import logger as imagesorcery_logger
from imagesorcery_mcp.middlewares.telemetry import TelemetryMiddleware


# Mock the awaitable response for call_next
async def mock_call_next_func(context):
    """A simple async function to mock the call_next behavior."""
    return "response"

# Mock the telemetry handlers to prevent actual network calls during tests
class MockAmplitudeHandler:
    def __init__(self):
        self.events = []

    def track_event(self, event_data):
        self.events.append(event_data)

class MockPostHogHandler:
    def __init__(self):
        self.events = []

    def track_event(self, event_data):
        self.events.append(event_data)


class TestTelemetryMiddleware:
    """Tests for the TelemetryMiddleware."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Ensure a config.toml exists for get_config()
        config_manager = get_config_manager()
        config_manager._ensure_config_file_exists()

        # Create a .user_id file for testing
        self.user_id_file = Path(".user_id")
        self.test_user_id = str(uuid.uuid4())
        self.user_id_file.write_text(self.test_user_id)

        # Reset global config manager to ensure fresh load with temp config
        import imagesorcery_mcp.config
        imagesorcery_mcp.config._config_manager = None
        get_config_manager().reset_runtime_overrides() # Ensure config is reloaded

        # Suppress logging during tests to avoid clutter
        logging.disable(logging.CRITICAL)

        # Initialize mock handlers for each test run
        self._mock_amplitude_handler = MockAmplitudeHandler()
        self._mock_posthog_handler = MockPostHogHandler()

    def teardown_method(self):
        """Clean up test environment."""
        logging.disable(logging.NOTSET) # Re-enable logging
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)

        # Reset global config manager again for other tests
        import imagesorcery_mcp.config
        imagesorcery_mcp.config._config_manager = None

    def test_middleware_initialization(self):
        """Test that TelemetryMiddleware can be initialized."""
        # Patch the module-level handlers during initialization
        with patch('imagesorcery_mcp.middlewares.telemetry.amplitude_handler', new=self._mock_amplitude_handler), \
             patch('imagesorcery_mcp.middlewares.telemetry.posthog_handler', new=self._mock_posthog_handler):
            middleware = TelemetryMiddleware(logger=imagesorcery_logger)
            assert isinstance(middleware, TelemetryMiddleware)
            assert middleware.user_id == self.test_user_id
            assert middleware.version != "unknown"  # Should get a version from pyproject.toml
            assert middleware.system is not None

    async def test_telemetry_tracking_enabled_and_disabled(self):
        """Test that telemetry events are tracked when enabled and not tracked when disabled."""
        # Patch the module-level handlers for this test
        with patch('imagesorcery_mcp.middlewares.telemetry.amplitude_handler', new=self._mock_amplitude_handler), \
             patch('imagesorcery_mcp.middlewares.telemetry.posthog_handler', new=self._mock_posthog_handler):

            middleware = TelemetryMiddleware(logger=imagesorcery_logger)
            config_manager = get_config_manager()

            # 1. Test when telemetry is DISABLED (default)
            config_manager.update_config({"telemetry.enabled": False}, persist=True)
            await middleware.on_call_tool(
                context=type("MockContext", (object,), {"message": type("MockMessage", (object,), {"name": "test_tool"})})(),
                call_next=mock_call_next_func
            )
            assert len(self._mock_amplitude_handler.events) == 0
            assert len(self._mock_posthog_handler.events) == 0

            # 2. Test when telemetry is ENABLED
            config_manager.update_config({"telemetry.enabled": True}, persist=True)
            await middleware.on_call_tool(
                context=type("MockContext", (object,), {"message": type("MockMessage", (object,), {"name": "test_tool"})})(),
                call_next=mock_call_next_func
            )
            assert len(self._mock_amplitude_handler.events) == 1
            assert len(self._mock_posthog_handler.events) == 1
            
            # Verify event data
            amplitude_event = self._mock_amplitude_handler.events[0]
            posthog_event = self._mock_posthog_handler.events[0]

            assert amplitude_event["user_id"] == self.test_user_id
            assert amplitude_event["action_type"] == "calling_tool"
            assert amplitude_event["identifier"] == "test_tool"
            assert amplitude_event["status"] == "success"

            assert posthog_event["user_id"] == self.test_user_id
            assert posthog_event["action_type"] == "calling_tool"
            assert posthog_event["identifier"] == "test_tool"
            assert posthog_event["status"] == "success"

            # 3. Test when telemetry is DISABLED again
            config_manager.update_config({"telemetry.enabled": False}, persist=True)
            self._mock_amplitude_handler.events = [] # Clear previous events
            self._mock_posthog_handler.events = []
            await middleware.on_call_tool(
                context=type("MockContext", (object,), {"message": type("MockMessage", (object,), {"name": "another_tool"})})(),
                call_next=mock_call_next_func
            )
            assert len(self._mock_amplitude_handler.events) == 0
            assert len(self._mock_posthog_handler.events) == 0
