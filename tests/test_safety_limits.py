"""Tests for the safety limits module."""

import pytest

from halo_track.safety.limits import SafetyLimits


class TestSafetyLimits:
    """Tests for the SafetyLimits class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.limits = SafetyLimits(
            min_pace_seconds=180,
            max_pace_seconds=900,
            max_brightness=255,
            min_brightness=10,
            emergency_stop_enabled=True,
        )

    def test_initialization(self):
        """Test safety limits initialization."""
        assert self.limits.min_pace_seconds == 180
        assert self.limits.max_pace_seconds == 900
        assert self.limits.max_brightness == 255
        assert self.limits.min_brightness == 10
        assert self.limits.emergency_stop_enabled is True

    def test_validate_pace_within_limits(self):
        """Test pace validation within limits."""
        is_valid, value, message = self.limits.validate_pace(480)
        assert is_valid is True
        assert value == 480

    def test_validate_pace_below_minimum(self):
        """Test pace validation below minimum."""
        is_valid, value, message = self.limits.validate_pace(120)
        assert is_valid is False
        assert value == 180  # Clamped to minimum
        assert "below minimum" in message

    def test_validate_pace_above_maximum(self):
        """Test pace validation above maximum."""
        is_valid, value, message = self.limits.validate_pace(1000)
        assert is_valid is False
        assert value == 900  # Clamped to maximum
        assert "above maximum" in message

    def test_validate_brightness_within_limits(self):
        """Test brightness validation within limits."""
        is_valid, value, message = self.limits.validate_brightness(128)
        assert is_valid is True
        assert value == 128

    def test_validate_brightness_below_minimum(self):
        """Test brightness validation below minimum."""
        is_valid, value, message = self.limits.validate_brightness(5)
        assert is_valid is False
        assert value == 10

    def test_validate_brightness_above_maximum(self):
        """Test brightness validation above maximum."""
        is_valid, value, message = self.limits.validate_brightness(300)
        assert is_valid is False
        assert value == 255

    def test_clamp_pace(self):
        """Test pace clamping."""
        assert self.limits.clamp_pace(100) == 180
        assert self.limits.clamp_pace(480) == 480
        assert self.limits.clamp_pace(1000) == 900

    def test_clamp_brightness(self):
        """Test brightness clamping."""
        assert self.limits.clamp_brightness(5) == 10
        assert self.limits.clamp_brightness(128) == 128
        assert self.limits.clamp_brightness(300) == 255

    def test_emergency_stop(self):
        """Test emergency stop functionality."""
        assert self.limits.is_emergency_stop_active() is False

        result = self.limits.trigger_emergency_stop()
        assert result is True
        assert self.limits.is_emergency_stop_active() is True

        self.limits.reset_emergency_stop()
        assert self.limits.is_emergency_stop_active() is False

    def test_emergency_stop_disabled(self):
        """Test emergency stop when disabled."""
        limits = SafetyLimits(emergency_stop_enabled=False)
        result = limits.trigger_emergency_stop()
        assert result is False
        assert limits.is_emergency_stop_active() is False

    def test_get_safe_pace_range(self):
        """Test getting safe pace range."""
        min_pace, max_pace = self.limits.get_safe_pace_range()
        assert min_pace == 180
        assert max_pace == 900

    def test_get_safe_brightness_range(self):
        """Test getting safe brightness range."""
        min_brightness, max_brightness = self.limits.get_safe_brightness_range()
        assert min_brightness == 10
        assert max_brightness == 255

    def test_get_status(self):
        """Test getting safety status."""
        status = self.limits.get_status()
        assert "emergency_stop_enabled" in status
        assert "emergency_stop_active" in status
        assert "min_pace_seconds" in status
        assert "max_pace_seconds" in status
