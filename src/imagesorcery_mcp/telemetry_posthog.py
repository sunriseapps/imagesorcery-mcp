import logging
import os
from typing import Any, Dict

from posthog import Posthog

from imagesorcery_mcp.telemetry_keys import POSTHOG_API_KEY

POSTHOG_HOST = "https://us.i.posthog.com"


class PostHogHandler:
    """Handles sending telemetry events to PostHog."""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("imagesorcery.telemetry.posthog")
        self.logger.debug("Initializing PostHog handler")
        
        api_key = self._get_api_key()
        
        if not api_key:
            self.enabled = False
            self.logger.warning("PostHog API key is not set. PostHog telemetry will be disabled.")
            self.logger.debug("PostHog telemetry disabled due to missing API key")
        else:
            self.enabled = True
            self.posthog_client = Posthog(api_key, host=POSTHOG_HOST)
            self.logger.info("PostHog handler initialized.")
            self.logger.debug(f"PostHog handler enabled with API key: {api_key}")

    def _get_api_key(self) -> str:
        """Get PostHog API key.

        Priority:
        1. Environment variable IMAGESORCERY_POSTHOG_API_KEY
        2. Value from src/imagesorcery_mcp/telemetry_keys.py (POSTHOG_API_KEY)
        """
        return os.environ.get('IMAGESORCERY_POSTHOG_API_KEY', POSTHOG_API_KEY)

    def track_event(self, event_data: Dict[str, Any]):
        """
        Tracks an event using PostHog.

        Args:
            event_data: A dictionary containing event properties.
                        Expected keys: 'user_id', 'action_type', 'identifier', 'status', etc.
        """
        if not self.enabled:
            self.logger.debug("PostHog telemetry disabled, skipping event tracking")
            return
            
        # Skip telemetry if DISABLE_TELEMETRY environment variable is set
        if os.environ.get('DISABLE_TELEMETRY', '').lower() in ('true', '1', 'yes'):
            self.logger.debug("Posthog telemetry disabled via environment variable")
            return

        try:
            user_id = event_data.get("user_id", "anonymous")
            event_type = f"mcp_{event_data.get('action_type', 'unknown_action')}"
            
            self.logger.debug(f"Preparing to track PostHog event: {event_type} for user {user_id}")
            self.logger.debug(f"Event data: {event_data}")

            self.posthog_client.capture(event_type, distinct_id=user_id, properties=event_data)
            self.logger.debug(f"Successfully tracked PostHog event: {event_type} for user {user_id}")

        except Exception as e:
            self.logger.error(f"Failed to send event to PostHog: {e}", exc_info=True)
            self.logger.debug(f"Event data that failed: {event_data}")


posthog_handler = PostHogHandler()
