"""Tests for the LED strip module."""

import pytest

from halo_track.devices.led_strip import LEDStrip


class TestLEDStrip:
    """Tests for the LEDStrip class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.strip = LEDStrip(
            led_count=10,
            gpio_pin=18,
            brightness=255,
            simulation_mode=True,
        )
        self.strip.initialize()

    def test_initialization(self):
        """Test LED strip initialization."""
        assert self.strip.led_count == 10
        assert self.strip.gpio_pin == 18
        assert self.strip.brightness == 255
        assert self.strip.is_initialized() is True

    def test_set_pixel(self):
        """Test setting individual pixel color."""
        result = self.strip.set_pixel(0, (255, 0, 0))
        assert result is True

        color = self.strip.get_pixel(0)
        assert color == (255, 0, 0)

    def test_set_pixel_out_of_range(self):
        """Test setting pixel out of range."""
        result = self.strip.set_pixel(100, (255, 0, 0))
        assert result is False

    def test_set_pixel_clamps_values(self):
        """Test that pixel values are clamped to 0-255."""
        self.strip.set_pixel(0, (300, -10, 128))
        color = self.strip.get_pixel(0)
        assert color == (255, 0, 128)

    def test_fill(self):
        """Test filling all pixels with a color."""
        self.strip.fill((0, 255, 0))

        for i in range(self.strip.led_count):
            color = self.strip.get_pixel(i)
            assert color == (0, 255, 0)

    def test_clear(self):
        """Test clearing all pixels."""
        self.strip.fill((255, 255, 255))
        self.strip.clear()

        for i in range(self.strip.led_count):
            color = self.strip.get_pixel(i)
            assert color == (0, 0, 0)

    def test_set_brightness(self):
        """Test setting brightness."""
        self.strip.set_brightness(128)
        assert self.strip.brightness == 128

    def test_get_led_count(self):
        """Test getting LED count."""
        assert self.strip.get_led_count() == 10

    def test_get_virtual_state(self):
        """Test getting virtual LED state."""
        self.strip.set_pixel(0, (255, 0, 0))
        self.strip.set_pixel(1, (0, 255, 0))

        state = self.strip.get_virtual_state()
        assert len(state) == 10
        assert state[0] == (255, 0, 0)
        assert state[1] == (0, 255, 0)

    def test_cleanup(self):
        """Test cleanup."""
        self.strip.cleanup()
        assert self.strip.is_initialized() is False
