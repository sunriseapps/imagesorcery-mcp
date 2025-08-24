import logging
import os
from typing import Any, Dict

from amplitude import Amplitude, BaseEvent

from imagesorcery_mcp.telemetry_keys import AMPLITUDE_API_KEY


class AmplitudeHandler:
    """Handles sending telemetry events to Amplitude."""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("imagesorcery.telemetry.amplitude")
        self.logger.debug("Initializing Amplitude handler")
        
        api_key = self._get_api_key()
        
        if not api_key:
            self.amplitude = None
            self.logger.warning("Amplitude API key is not set. Amplitude telemetry will be disabled.")
            self.logger.debug("Amplitude telemetry disabled due to missing API key")
        else:
            self.amplitude = Amplitude(api_key)
            self.logger.info("Amplitude handler initialized.")
            self.logger.debug(f"Amplitude handler enabled with API key: {api_key}")

    def _get_api_key(self) -> str:
        """Get Amplitude API key.

        Priority:
        1. Environment variable IMAGESORCERY_AMPLITUDE_API_KEY
        2. Value from src/imagesorcery_mcp/telemetry_keys.py (AMPLITUDE_API_KEY)
        """
        return os.environ.get('IMAGESORCERY_AMPLITUDE_API_KEY', AMPLITUDE_API_KEY)

    def track_event(self, event_data: Dict[str, Any]):
        """
        Tracks an event using Amplitude.

        Args:
            event_data: A dictionary containing event properties.
                        Expected keys: 'user_id', 'action_type', 'identifier', 'status', etc.
        """
        if not self.amplitude:
            self.logger.debug("Amplitude telemetry disabled, skipping event tracking")
            return
            
        # Skip telemetry if DISABLE_TELEMETRY environment variable is set
        if os.environ.get('DISABLE_TELEMETRY', '').lower() in ('true', '1', 'yes'):
            self.logger.debug("Amplitude telemetry disabled via environment variable")
            return

        try:
            user_id = event_data.get("user_id", "anonymous")
            event_type = f"mcp_{event_data.get('action_type', 'unknown_action')}"
            
            self.logger.debug(f"Preparing to track Amplitude event: {event_type} for user {user_id}")
            self.logger.debug(f"Event data: {event_data}")

            event = BaseEvent(event_type=event_type, user_id=user_id, event_properties=event_data)

            self.amplitude.track(event)
            self.logger.debug(f"Successfully tracked Amplitude event: {event_type} for user {user_id}")

        except Exception as e:
            self.logger.error(f"Failed to send event to Amplitude: {e}", exc_info=True)
            self.logger.debug(f"Event data that failed: {event_data}")


# Global instance to be used by other modules
amplitude_handler = AmplitudeHandler()
