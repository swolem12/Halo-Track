"""Tests for the utility helpers module."""

import pytest

from halo_track.utils.helpers import (
    pace_to_seconds,
    seconds_to_pace,
    validate_pace_format,
    format_time_mmss,
    format_time_hhmmss,
    calculate_distance_km,
    clamp,
    lerp,
    map_range,
)


class TestPaceConversion:
    """Tests for pace conversion functions."""

    def test_pace_to_seconds_valid(self):
        """Test valid pace string conversion."""
        assert pace_to_seconds("8:00") == 480
        assert pace_to_seconds("5:30") == 330
        assert pace_to_seconds("12:45") == 765
        assert pace_to_seconds("0:30") == 30

    def test_pace_to_seconds_invalid(self):
        """Test invalid pace string conversion."""
        with pytest.raises(ValueError):
            pace_to_seconds("invalid")

        with pytest.raises(ValueError):
            pace_to_seconds("8:60")  # Invalid seconds

    def test_seconds_to_pace(self):
        """Test seconds to pace string conversion."""
        assert seconds_to_pace(480) == "8:00"
        assert seconds_to_pace(330) == "5:30"
        assert seconds_to_pace(765) == "12:45"

    def test_seconds_to_pace_negative(self):
        """Test negative seconds raises error."""
        with pytest.raises(ValueError):
            seconds_to_pace(-1)


class TestValidatePaceFormat:
    """Tests for pace format validation."""

    def test_valid_formats(self):
        """Test valid pace formats."""
        assert validate_pace_format("8:00") is True
        assert validate_pace_format("12:30") is True
        assert validate_pace_format("5:00") is True
        assert validate_pace_format("0:30") is True

    def test_invalid_formats(self):
        """Test invalid pace formats."""
        assert validate_pace_format("8") is False
        assert validate_pace_format("8:0") is False
        assert validate_pace_format("8:000") is False
        assert validate_pace_format("invalid") is False
        assert validate_pace_format("") is False
        assert validate_pace_format(None) is False


class TestTimeFormatting:
    """Tests for time formatting functions."""

    def test_format_time_mmss(self):
        """Test MM:SS formatting."""
        assert format_time_mmss(90) == "01:30"
        assert format_time_mmss(0) == "00:00"
        assert format_time_mmss(3661) == "61:01"

    def test_format_time_hhmmss(self):
        """Test HH:MM:SS formatting."""
        assert format_time_hhmmss(90) == "1:30"
        assert format_time_hhmmss(3661) == "1:01:01"
        assert format_time_hhmmss(7322) == "2:02:02"


class TestDistanceCalculation:
    """Tests for distance calculation."""

    def test_calculate_distance_km(self):
        """Test distance calculation."""
        # At 480s/km pace, 480 seconds = 1km
        assert calculate_distance_km(480, 480) == 1.0

        # At 480s/km pace, 240 seconds = 0.5km
        assert calculate_distance_km(480, 240) == 0.5

    def test_calculate_distance_km_zero_pace(self):
        """Test distance calculation with zero pace."""
        assert calculate_distance_km(0, 100) == 0.0


class TestMathHelpers:
    """Tests for math helper functions."""

    def test_clamp(self):
        """Test value clamping."""
        assert clamp(5, 0, 10) == 5
        assert clamp(-5, 0, 10) == 0
        assert clamp(15, 0, 10) == 10

    def test_lerp(self):
        """Test linear interpolation."""
        assert lerp(0, 10, 0) == 0
        assert lerp(0, 10, 1) == 10
        assert lerp(0, 10, 0.5) == 5

    def test_lerp_clamped(self):
        """Test lerp with values outside 0-1."""
        assert lerp(0, 10, -0.5) == 0
        assert lerp(0, 10, 1.5) == 10

    def test_map_range(self):
        """Test range mapping."""
        # Map 5 from 0-10 to 0-100
        assert map_range(5, 0, 10, 0, 100) == 50

        # Map 0 from 0-10 to 0-100
        assert map_range(0, 0, 10, 0, 100) == 0

        # Map 10 from 0-10 to 0-100
        assert map_range(10, 0, 10, 0, 100) == 100
