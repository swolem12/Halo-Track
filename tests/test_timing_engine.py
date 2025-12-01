"""Tests for the timing engine module."""

import pytest

from halo_track.engine.timing_engine import TimingEngine, TimingParameters


class TestTimingEngine:
    """Tests for the TimingEngine class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TimingEngine(
            track_length_meters=400.0,
            led_count=60,
            leds_per_meter=30.0,
        )

    def test_initialization(self):
        """Test timing engine initialization."""
        assert self.engine.track_length_meters == 400.0
        assert self.engine.led_count == 60
        assert self.engine.leds_per_meter == 30.0

    def test_calculate_timing_8min_pace(self):
        """Test timing calculation for 8:00 min/km pace."""
        # 8:00 min/km = 480 seconds/km
        timing = self.engine.calculate_timing(480)

        assert timing.pace_seconds_per_km == 480
        # Speed: 1000m / 480s ≈ 2.083 m/s
        assert abs(timing.meters_per_second - 2.083) < 0.01
        # LEDs per second: 2.083 m/s * 30 LEDs/m ≈ 62.5 LEDs/s
        assert abs(timing.leds_per_second - 62.5) < 0.1
        # LED interval: 1000ms / 62.5 ≈ 16ms
        assert abs(timing.led_interval_ms - 16.0) < 0.5

    def test_calculate_timing_5min_pace(self):
        """Test timing calculation for 5:00 min/km pace (fast)."""
        timing = self.engine.calculate_timing(300)

        assert timing.pace_seconds_per_km == 300
        # Speed: 1000m / 300s ≈ 3.333 m/s
        assert abs(timing.meters_per_second - 3.333) < 0.01

    def test_calculate_timing_12min_pace(self):
        """Test timing calculation for 12:00 min/km pace (slow)."""
        timing = self.engine.calculate_timing(720)

        assert timing.pace_seconds_per_km == 720
        # Speed: 1000m / 720s ≈ 1.389 m/s
        assert abs(timing.meters_per_second - 1.389) < 0.01

    def test_pace_to_led_interval_ms(self):
        """Test direct pace to LED interval conversion."""
        interval = self.engine.pace_to_led_interval_ms(480)
        # For 8:00 pace, interval should be around 16ms
        assert 10 < interval < 20

    def test_pace_to_speed_mps(self):
        """Test pace to speed conversion."""
        speed = self.engine.pace_to_speed_mps(480)
        assert abs(speed - 2.083) < 0.01

    def test_speed_to_pace(self):
        """Test speed to pace conversion."""
        pace = self.engine.speed_to_pace(2.083)
        assert abs(pace - 480) < 5

    def test_get_led_position_at_time(self):
        """Test LED position calculation."""
        # At 480s/km pace, after 1 second we should move ~62.5 LEDs
        position = self.engine.get_led_position_at_time(1.0, 480)
        # Position should wrap around (60 LEDs)
        assert 0 <= position < 60

    def test_get_distance_at_time(self):
        """Test distance calculation."""
        # At 480s/km pace, in 480 seconds we travel 1km = 1000m
        distance = self.engine.get_distance_at_time(480, 480)
        assert abs(distance - 1000.0) < 1

    def test_get_lap_count_at_time(self):
        """Test lap counting."""
        # For 400m track at 480s/km pace
        # Time for one lap: 400m / (1000/480 m/s) = 400 * 480 / 1000 = 192s
        laps, progress = self.engine.get_lap_count_at_time(192, 480)
        assert laps == 1
        assert abs(progress) < 0.01

    def test_format_pace(self):
        """Test pace formatting."""
        assert self.engine.format_pace(480) == "8:00 min/km"
        assert self.engine.format_pace(300) == "5:00 min/km"
        assert self.engine.format_pace(450) == "7:30 min/km"

    def test_format_time(self):
        """Test time formatting."""
        assert self.engine.format_time(90) == "1:30"
        assert self.engine.format_time(3661) == "1:01:01"


class TestTimingParameters:
    """Tests for TimingParameters dataclass."""

    def test_creation(self):
        """Test TimingParameters creation."""
        params = TimingParameters(
            pace_seconds_per_km=480,
            led_interval_ms=16.0,
            leds_per_second=62.5,
            meters_per_second=2.083,
            track_lap_time_seconds=192.0,
        )

        assert params.pace_seconds_per_km == 480
        assert params.led_interval_ms == 16.0
        assert params.leds_per_second == 62.5
        assert params.meters_per_second == 2.083
        assert params.track_lap_time_seconds == 192.0
