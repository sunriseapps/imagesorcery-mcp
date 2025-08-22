import logging
import os
from typing import Any, Dict

from posthog import Posthog

POSTHOG_API_KEY = "phc_AS788x1ftlVzRCJ5NlnaKIPkJ4PyXKKejsAb8x6dl5X"
POSTHOG_HOST = "https://us.i.posthog.com"

# Global instance for PostHog
posthog_instance = Posthog(POSTHOG_API_KEY, host=POSTHOG_HOST)


class PostHogHandler:
    """Handles sending telemetry events to PostHog."""

    def __init__(self, posthog_client: Posthog, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("imagesorcery.telemetry.posthog")
        self.logger.debug("Initializing PostHog handler")
        
        if not posthog_client.api_key:
            self.enabled = False
            self.logger.warning("PostHog API key is not set. PostHog telemetry will be disabled.")
            self.logger.debug("PostHog telemetry disabled due to missing API key")
        else:
            self.enabled = True
            self.posthog_client = posthog_client
            self.logger.info("PostHog handler initialized.")
            self.logger.debug(f"PostHog handler enabled with API key: {posthog_client.api_key[:8]}...")

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


posthog_handler = PostHogHandler(posthog_client=posthog_instance)
