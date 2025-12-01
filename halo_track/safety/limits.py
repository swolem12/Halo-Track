"""
Safety Limits for Halo Track.

Provides validation and safety limits for the pacing system.
"""

import logging

logger = logging.getLogger(__name__)


class SafetyLimits:
    """
    Manages safety limits and validation for the Halo Track system.

    Ensures that pace values, brightness settings, and other parameters
    remain within safe operating ranges.
    """

    def __init__(
        self,
        min_pace_seconds: int = 180,
        max_pace_seconds: int = 900,
        max_brightness: int = 255,
        min_brightness: int = 10,
        emergency_stop_enabled: bool = True,
    ):
        """
        Initialize safety limits.

        Args:
            min_pace_seconds: Minimum pace (fastest, e.g., 3:00 min/km).
            max_pace_seconds: Maximum pace (slowest, e.g., 15:00 min/km).
            max_brightness: Maximum LED brightness (0-255).
            min_brightness: Minimum LED brightness (0-255).
            emergency_stop_enabled: Enable emergency stop functionality.
        """
        self.min_pace_seconds = min_pace_seconds
        self.max_pace_seconds = max_pace_seconds
        self.max_brightness = max_brightness
        self.min_brightness = min_brightness
        self.emergency_stop_enabled = emergency_stop_enabled

        self._emergency_stop_active = False

        logger.info(
            "Safety limits initialized: pace=%d-%ds, brightness=%d-%d",
            min_pace_seconds,
            max_pace_seconds,
            min_brightness,
            max_brightness,
        )

    def validate_pace(self, pace_seconds: int) -> tuple:
        """
        Validate a pace value against safety limits.

        Args:
            pace_seconds: Pace in seconds per kilometer.

        Returns:
            Tuple of (is_valid, clamped_value, message).
        """
        if pace_seconds < self.min_pace_seconds:
            clamped = self.min_pace_seconds
            message = (
                f"Pace {pace_seconds}s is below minimum. "
                f"Clamped to {clamped}s ({self._format_pace(clamped)})"
            )
            logger.warning(message)
            return False, clamped, message

        if pace_seconds > self.max_pace_seconds:
            clamped = self.max_pace_seconds
            message = (
                f"Pace {pace_seconds}s is above maximum. "
                f"Clamped to {clamped}s ({self._format_pace(clamped)})"
            )
            logger.warning(message)
            return False, clamped, message

        return True, pace_seconds, "Pace is within safe limits"

    def validate_brightness(self, brightness: int) -> tuple:
        """
        Validate a brightness value against safety limits.

        Args:
            brightness: Brightness value (0-255).

        Returns:
            Tuple of (is_valid, clamped_value, message).
        """
        if brightness < self.min_brightness:
            clamped = self.min_brightness
            message = f"Brightness {brightness} is below minimum. Clamped to {clamped}"
            logger.warning(message)
            return False, clamped, message

        if brightness > self.max_brightness:
            clamped = self.max_brightness
            message = f"Brightness {brightness} is above maximum. Clamped to {clamped}"
            logger.warning(message)
            return False, clamped, message

        return True, brightness, "Brightness is within safe limits"

    def clamp_pace(self, pace_seconds: int) -> int:
        """
        Clamp a pace value to safe limits.

        Args:
            pace_seconds: Pace in seconds per kilometer.

        Returns:
            Clamped pace value.
        """
        return max(self.min_pace_seconds, min(self.max_pace_seconds, pace_seconds))

    def clamp_brightness(self, brightness: int) -> int:
        """
        Clamp a brightness value to safe limits.

        Args:
            brightness: Brightness value (0-255).

        Returns:
            Clamped brightness value.
        """
        return max(self.min_brightness, min(self.max_brightness, brightness))

    def trigger_emergency_stop(self) -> bool:
        """
        Trigger emergency stop.

        Returns:
            True if emergency stop was triggered, False if disabled.
        """
        if self.emergency_stop_enabled:
            self._emergency_stop_active = True
            logger.warning("EMERGENCY STOP TRIGGERED")
            return True

        logger.warning("Emergency stop is disabled")
        return False

    def reset_emergency_stop(self) -> None:
        """Reset the emergency stop state."""
        self._emergency_stop_active = False
        logger.info("Emergency stop reset")

    def is_emergency_stop_active(self) -> bool:
        """Check if emergency stop is active."""
        return self._emergency_stop_active

    def get_safe_pace_range(self) -> tuple:
        """
        Get the safe pace range.

        Returns:
            Tuple of (min_pace, max_pace) in seconds.
        """
        return self.min_pace_seconds, self.max_pace_seconds

    def get_safe_brightness_range(self) -> tuple:
        """
        Get the safe brightness range.

        Returns:
            Tuple of (min_brightness, max_brightness).
        """
        return self.min_brightness, self.max_brightness

    @staticmethod
    def _format_pace(pace_seconds: int) -> str:
        """Format pace as MM:SS."""
        minutes = pace_seconds // 60
        seconds = pace_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def get_status(self) -> dict:
        """
        Get the current safety system status.

        Returns:
            Dictionary with safety status information.
        """
        return {
            "emergency_stop_enabled": self.emergency_stop_enabled,
            "emergency_stop_active": self._emergency_stop_active,
            "min_pace_seconds": self.min_pace_seconds,
            "max_pace_seconds": self.max_pace_seconds,
            "min_brightness": self.min_brightness,
            "max_brightness": self.max_brightness,
        }
