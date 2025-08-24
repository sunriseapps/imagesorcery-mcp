import logging
import sys
from importlib.metadata import version
from typing import Any

from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext

from imagesorcery_mcp.config import get_config
from imagesorcery_mcp.telemetry_amplitude import amplitude_handler
from pathlib import Path
from imagesorcery_mcp.telemetry_posthog import posthog_handler


class TelemetryMiddleware(Middleware):
    """Middleware that logs every tool, prompt, and resource run based on configuration."""
    
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("imagesorcery.telemetry")
        self.user_id = self._get_user_id() # Added user_id
        self.version = self._get_version()
        self.system = sys.platform

        self.amplitude_handler = amplitude_handler
        self.posthog_handler = posthog_handler

    def _get_user_id(self) -> str:
        """Get user_id from .user_id file."""
        user_id_file = Path(".user_id")  # Path to .user_id in project root
        self.logger.debug(f"Looking for user ID file at: {user_id_file.absolute()}")
        try:
            if user_id_file.exists():
                user_id = user_id_file.read_text().strip()
                if user_id:
                    self.logger.debug(f"User ID from file: {user_id}")
                    return user_id
            self.logger.warning("User ID file not found or empty. Telemetry will use 'anonymous'.")
            return "anonymous"
        except Exception as e:
            self.logger.error(f"Could not read user_id: {e}")
            return "anonymous"

    def _get_version(self) -> str:
        """Get package version."""
        try:
            return version("imagesorcery-mcp")
        except Exception:
            self.logger.warning("Could not determine package version for telemetry.")
            return "unknown"

    async def _handle_action(self, action_type: str, identifier: str, context: MiddlewareContext, call_next: CallNext) -> Any:
        """Helper to log actions before and after execution, if telemetry is enabled."""
        self.logger.debug(f"{action_type}: {identifier}")
        config = get_config()
        self.logger.debug(f"Telemetry enabled: {config.telemetry.enabled}")

        if not config.telemetry.enabled:
            self.logger.debug("Telemetry enabled skipped")
            return await call_next(context)

        log_data = {
            "user_id": self.user_id, # Added user_id to log_data
            "version": self.version,
            "system": self.system,
            "action_type": action_type.lower().replace(" ", "_"),
            "identifier": identifier,
        }

        try:
            response = await call_next(context)
            log_data["status"] = "success"
            self.logger.info(log_data)
            self.posthog_handler.track_event(log_data)
            self.amplitude_handler.track_event(log_data)
            return response
        except Exception:
            log_data["status"] = "failed"
            self.logger.warning(log_data)
            self.posthog_handler.track_event(log_data)
            self.amplitude_handler.track_event(log_data)
            raise

    async def on_call_tool(self, context: MiddlewareContext, call_next: CallNext) -> Any:
        """Log tool calls before and after execution, if telemetry is enabled."""
        return await self._handle_action("Calling tool", context.message.name, context, call_next)

    async def on_read_resource(self, context: MiddlewareContext, call_next: CallNext) -> Any:
        """Log resource reads before and after execution, if telemetry is enabled."""
        return await self._handle_action("Reading resource", str(context.message.uri), context, call_next)

    async def on_get_prompt(self, context: MiddlewareContext, call_next: CallNext) -> Any:
        """Log prompt retrievals before and after execution, if telemetry is enabled."""
        return await self._handle_action("Getting prompt", context.message.name, context, call_next)
