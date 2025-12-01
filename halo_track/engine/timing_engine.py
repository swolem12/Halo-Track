"""
Timing Engine for Halo Track.

Converts running pace to LED chase speed and manages timing calculations.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TimingParameters:
    """Calculated timing parameters for LED pacing."""

    pace_seconds_per_km: int
    led_interval_ms: float
    leds_per_second: float
    meters_per_second: float
    track_lap_time_seconds: float


class TimingEngine:
    """
    Engine for converting running pace to LED timing.

    Calculates the timing parameters needed to drive the LED chase
    pattern at a speed that matches the target running pace.
    """

    def __init__(
        self,
        track_length_meters: float = 400.0,
        led_count: int = 60,
        leds_per_meter: float = 30.0,
    ):
        """
        Initialize the timing engine.

        Args:
            track_length_meters: Length of the running track in meters.
            led_count: Total number of LEDs in the strip.
            leds_per_meter: LED density per meter of track.
        """
        self.track_length_meters = track_length_meters
        self.led_count = led_count
        self.leds_per_meter = leds_per_meter

        logger.info(
            "Timing engine initialized: track=%.1fm, LEDs=%d, density=%.1f/m",
            track_length_meters,
            led_count,
            leds_per_meter,
        )

    def calculate_timing(self, pace_seconds_per_km: int) -> TimingParameters:
        """
        Calculate LED timing parameters for a given running pace.

        Args:
            pace_seconds_per_km: Target pace in seconds per kilometer.

        Returns:
            TimingParameters with calculated values.
        """
        # Calculate speed in meters per second
        meters_per_second = 1000.0 / pace_seconds_per_km

        # Calculate LEDs per second based on LED density and speed
        leds_per_second = meters_per_second * self.leds_per_meter

        # Calculate milliseconds per LED step
        led_interval_ms = 1000.0 / leds_per_second if leds_per_second > 0 else 0

        # Calculate lap time for the track
        track_lap_time_seconds = self.track_length_meters / meters_per_second

        timing = TimingParameters(
            pace_seconds_per_km=pace_seconds_per_km,
            led_interval_ms=led_interval_ms,
            leds_per_second=leds_per_second,
            meters_per_second=meters_per_second,
            track_lap_time_seconds=track_lap_time_seconds,
        )

        logger.debug(
            "Timing calculated: pace=%ds/km, interval=%.2fms, LEDs/s=%.2f",
            pace_seconds_per_km,
            led_interval_ms,
            leds_per_second,
        )

        return timing

    def pace_to_led_interval_ms(self, pace_seconds_per_km: int) -> float:
        """
        Convert pace to LED interval in milliseconds.

        This is the time between each LED step in the chase pattern.

        Args:
            pace_seconds_per_km: Target pace in seconds per kilometer.

        Returns:
            Milliseconds between LED steps.
        """
        timing = self.calculate_timing(pace_seconds_per_km)
        return timing.led_interval_ms

    def pace_to_speed_mps(self, pace_seconds_per_km: int) -> float:
        """
        Convert pace to speed in meters per second.

        Args:
            pace_seconds_per_km: Pace in seconds per kilometer.

        Returns:
            Speed in meters per second.
        """
        return 1000.0 / pace_seconds_per_km

    def speed_to_pace(self, meters_per_second: float) -> int:
        """
        Convert speed to pace.

        Args:
            meters_per_second: Speed in meters per second.

        Returns:
            Pace in seconds per kilometer.
        """
        if meters_per_second <= 0:
            return 0
        return int(1000.0 / meters_per_second)

    def get_led_position_at_time(
        self, elapsed_seconds: float, pace_seconds_per_km: int
    ) -> int:
        """
        Calculate LED position at a given elapsed time.

        Args:
            elapsed_seconds: Time elapsed since start.
            pace_seconds_per_km: Current pace in seconds per kilometer.

        Returns:
            LED index (0 to led_count - 1).
        """
        timing = self.calculate_timing(pace_seconds_per_km)
        total_leds_traveled = elapsed_seconds * timing.leds_per_second
        led_position = int(total_leds_traveled) % self.led_count
        return led_position

    def get_distance_at_time(
        self, elapsed_seconds: float, pace_seconds_per_km: int
    ) -> float:
        """
        Calculate distance traveled at a given elapsed time.

        Args:
            elapsed_seconds: Time elapsed since start.
            pace_seconds_per_km: Current pace in seconds per kilometer.

        Returns:
            Distance in meters.
        """
        meters_per_second = self.pace_to_speed_mps(pace_seconds_per_km)
        return elapsed_seconds * meters_per_second

    def get_lap_count_at_time(
        self, elapsed_seconds: float, pace_seconds_per_km: int
    ) -> tuple:
        """
        Calculate lap count and progress at a given elapsed time.

        Args:
            elapsed_seconds: Time elapsed since start.
            pace_seconds_per_km: Current pace in seconds per kilometer.

        Returns:
            Tuple of (complete_laps, lap_progress_fraction).
        """
        distance = self.get_distance_at_time(elapsed_seconds, pace_seconds_per_km)
        complete_laps = int(distance / self.track_length_meters)
        remaining = distance - (complete_laps * self.track_length_meters)
        lap_progress = remaining / self.track_length_meters
        return complete_laps, lap_progress

    def format_pace(self, pace_seconds_per_km: int) -> str:
        """
        Format pace as a human-readable string.

        Args:
            pace_seconds_per_km: Pace in seconds per kilometer.

        Returns:
            Formatted string (e.g., "8:00 min/km").
        """
        minutes = pace_seconds_per_km // 60
        seconds = pace_seconds_per_km % 60
        return f"{minutes}:{seconds:02d} min/km"

    def format_time(self, seconds: float) -> str:
        """
        Format time as a human-readable string.

        Args:
            seconds: Time in seconds.

        Returns:
            Formatted string (e.g., "1:30:45").
        """
        hours = int(seconds // 3600)
        remaining = seconds % 3600
        minutes = int(remaining // 60)
        secs = int(remaining % 60)

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
