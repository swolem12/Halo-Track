"""
Utility functions for Halo Track.

Provides helper functions for pace conversion and validation.
"""

import re


def pace_to_seconds(pace_str: str) -> int:
    """
    Convert a pace string to total seconds.

    Args:
        pace_str: Pace in format "M:SS" or "MM:SS" (e.g., "8:00", "12:30").

    Returns:
        Total seconds per kilometer.

    Raises:
        ValueError: If the pace format is invalid.
    """
    if not validate_pace_format(pace_str):
        raise ValueError(f"Invalid pace format: {pace_str}")

    parts = pace_str.split(":")
    minutes = int(parts[0])
    seconds = int(parts[1])

    if seconds >= 60:
        raise ValueError(f"Seconds must be less than 60: {pace_str}")

    return minutes * 60 + seconds


def seconds_to_pace(total_seconds: int) -> str:
    """
    Convert total seconds to a pace string.

    Args:
        total_seconds: Total seconds per kilometer.

    Returns:
        Formatted pace string (e.g., "8:00").
    """
    if total_seconds < 0:
        raise ValueError("Seconds cannot be negative")

    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


def validate_pace_format(pace_str: str) -> bool:
    """
    Validate that a string is in valid pace format.

    Args:
        pace_str: String to validate.

    Returns:
        True if valid, False otherwise.
    """
    if not pace_str or not isinstance(pace_str, str):
        return False

    pattern = r"^\d{1,2}:\d{2}$"
    return bool(re.match(pattern, pace_str))


def format_time_mmss(seconds: float) -> str:
    """
    Format seconds as MM:SS.

    Args:
        seconds: Time in seconds.

    Returns:
        Formatted time string.
    """
    total_seconds = int(seconds)
    mins = total_seconds // 60
    secs = total_seconds % 60
    return f"{mins:02d}:{secs:02d}"


def format_time_hhmmss(seconds: float) -> str:
    """
    Format seconds as HH:MM:SS.

    Args:
        seconds: Time in seconds.

    Returns:
        Formatted time string.
    """
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    remaining = total_seconds % 3600
    mins = remaining // 60
    secs = remaining % 60

    if hours > 0:
        return f"{hours}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"


def calculate_distance_km(pace_seconds: int, elapsed_seconds: float) -> float:
    """
    Calculate distance traveled based on pace and time.

    Args:
        pace_seconds: Pace in seconds per kilometer.
        elapsed_seconds: Time elapsed in seconds.

    Returns:
        Distance in kilometers.
    """
    if pace_seconds <= 0:
        return 0.0
    return elapsed_seconds / pace_seconds


def calculate_eta_seconds(
    pace_seconds: int, distance_km: float, current_distance_km: float
) -> float:
    """
    Calculate estimated time to arrival (ETA).

    Args:
        pace_seconds: Pace in seconds per kilometer.
        distance_km: Total distance in kilometers.
        current_distance_km: Current distance traveled in kilometers.

    Returns:
        ETA in seconds.
    """
    remaining_distance = max(0, distance_km - current_distance_km)
    return remaining_distance * pace_seconds


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value to a range.

    Args:
        value: Value to clamp.
        min_value: Minimum allowed value.
        max_value: Maximum allowed value.

    Returns:
        Clamped value.
    """
    return max(min_value, min(max_value, value))


def lerp(start: float, end: float, t: float) -> float:
    """
    Linear interpolation between two values.

    Args:
        start: Start value.
        end: End value.
        t: Interpolation factor (0-1).

    Returns:
        Interpolated value.
    """
    t = clamp(t, 0.0, 1.0)
    return start + (end - start) * t


def map_range(
    value: float,
    in_min: float,
    in_max: float,
    out_min: float,
    out_max: float,
) -> float:
    """
    Map a value from one range to another.

    Args:
        value: Input value.
        in_min: Input range minimum.
        in_max: Input range maximum.
        out_min: Output range minimum.
        out_max: Output range maximum.

    Returns:
        Mapped value in output range.
    """
    if in_max == in_min:
        return out_min

    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
