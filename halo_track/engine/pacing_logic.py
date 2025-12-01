"""
LED Pacing Logic for Halo Track.

Implements the LED chase patterns and pacing visualization logic.
"""

import logging
import math
import time
from enum import Enum
from typing import Tuple, Optional

from ..devices.led_strip import LEDStrip

logger = logging.getLogger(__name__)


class PacingMode(Enum):
    """LED pacing display modes."""

    CHASE = "chase"
    PULSE = "pulse"
    SOLID = "solid"
    RAINBOW = "rainbow"
    OFF = "off"


class PacingLogic:
    """
    Controls LED pacing patterns for running guidance.

    Manages the visual representation of the target pace on the LED strip.
    """

    # Color presets
    COLOR_GREEN = (0, 255, 0)
    COLOR_RED = (255, 0, 0)
    COLOR_BLUE = (0, 0, 255)
    COLOR_YELLOW = (255, 255, 0)
    COLOR_WHITE = (255, 255, 255)
    COLOR_OFF = (0, 0, 0)

    def __init__(
        self,
        led_strip: LEDStrip,
        chase_length: int = 5,
        primary_color: Tuple[int, int, int] = None,
        tail_fade: bool = True,
    ):
        """
        Initialize pacing logic.

        Args:
            led_strip: LEDStrip instance for output.
            chase_length: Number of LEDs in the chase pattern.
            primary_color: Primary color for the chase (default: green).
            tail_fade: Whether to fade the tail of the chase pattern.
        """
        self.led_strip = led_strip
        self.chase_length = chase_length
        self.primary_color = primary_color or self.COLOR_GREEN
        self.tail_fade = tail_fade

        self._mode = PacingMode.CHASE
        self._position = 0
        self._running = False
        self._last_update_time = 0
        self._led_interval_ms = 100

    def set_mode(self, mode: PacingMode) -> None:
        """
        Set the pacing display mode.

        Args:
            mode: The PacingMode to use.
        """
        self._mode = mode
        logger.info("Pacing mode set to: %s", mode.value)

    def get_mode(self) -> PacingMode:
        """Get the current pacing mode."""
        return self._mode

    def set_led_interval(self, interval_ms: float) -> None:
        """
        Set the LED step interval.

        Args:
            interval_ms: Milliseconds between LED steps.
        """
        self._led_interval_ms = max(1, interval_ms)
        logger.debug("LED interval set to: %.2f ms", self._led_interval_ms)

    def set_color(self, color: Tuple[int, int, int]) -> None:
        """
        Set the primary chase color.

        Args:
            color: RGB color tuple.
        """
        self.primary_color = color

    def start(self) -> None:
        """Start the pacing animation."""
        self._running = True
        self._last_update_time = time.time()
        self._position = 0
        logger.info("Pacing animation started")

    def stop(self) -> None:
        """Stop the pacing animation."""
        self._running = False
        self.led_strip.clear()
        logger.info("Pacing animation stopped")

    def reset(self) -> None:
        """Reset the pacing animation to the starting position."""
        self._position = 0
        self._last_update_time = time.time()
        self.led_strip.clear()

    def is_running(self) -> bool:
        """Check if the pacing animation is running."""
        return self._running

    def update(self) -> bool:
        """
        Update the LED display based on elapsed time.

        Returns:
            True if the display was updated, False otherwise.
        """
        if not self._running:
            return False

        current_time = time.time()
        elapsed_ms = (current_time - self._last_update_time) * 1000

        if elapsed_ms >= self._led_interval_ms:
            self._advance_position()
            self._render()
            self._last_update_time = current_time
            return True

        return False

    def _advance_position(self) -> None:
        """Advance the chase position by one LED."""
        self._position = (self._position + 1) % self.led_strip.get_led_count()

    def _render(self) -> None:
        """Render the current mode to the LED strip."""
        if self._mode == PacingMode.CHASE:
            self._render_chase()
        elif self._mode == PacingMode.PULSE:
            self._render_pulse()
        elif self._mode == PacingMode.SOLID:
            self._render_solid()
        elif self._mode == PacingMode.RAINBOW:
            self._render_rainbow()
        elif self._mode == PacingMode.OFF:
            self.led_strip.clear()

        self.led_strip.show()

    def _render_chase(self) -> None:
        """Render the chase pattern."""
        led_count = self.led_strip.get_led_count()

        # Clear all LEDs first
        for i in range(led_count):
            self.led_strip.set_pixel(i, self.COLOR_OFF)

        # Draw the chase pattern with optional tail fade
        for offset in range(self.chase_length):
            led_idx = (self._position - offset) % led_count

            if self.tail_fade and offset > 0:
                # Calculate fade factor
                fade_factor = 1.0 - (offset / self.chase_length)
                color = tuple(int(c * fade_factor) for c in self.primary_color)
            else:
                color = self.primary_color

            self.led_strip.set_pixel(led_idx, color)

    def _render_pulse(self) -> None:
        """Render a pulsing pattern."""
        led_count = self.led_strip.get_led_count()

        # Calculate pulse phase based on LED position (0 to 2*pi for full cycle)
        pulse_phase = (self._position / led_count) * 2 * math.pi

        # Create smooth breathing effect using triangle wave
        # Maps phase to brightness: 0->0.5, 1->1, 2->0.5 (repeating)
        brightness = self._calculate_pulse_brightness(pulse_phase)

        color = tuple(int(c * brightness) for c in self.primary_color)

        for i in range(led_count):
            self.led_strip.set_pixel(i, color)

    @staticmethod
    def _calculate_pulse_brightness(phase: float) -> float:
        """
        Calculate pulse brightness from phase using triangle wave.

        Args:
            phase: Phase value in radians.

        Returns:
            Brightness value between 0.5 and 1.0.
        """
        # Normalize phase to 0-2 range and create triangle wave
        normalized = phase % 2
        triangle_value = abs(normalized - 1)
        # Scale to 0.5-1.0 range for visible breathing effect
        return 0.5 + (triangle_value * 0.5)

    def _render_solid(self) -> None:
        """Render a solid color."""
        self.led_strip.fill(self.primary_color)

    def _render_rainbow(self) -> None:
        """Render a rainbow pattern."""
        led_count = self.led_strip.get_led_count()

        for i in range(led_count):
            # Calculate hue based on position
            hue = ((i + self._position) % led_count) / led_count
            color = self._hsv_to_rgb(hue, 1.0, 1.0)
            self.led_strip.set_pixel(i, color)

    @staticmethod
    def _hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        """
        Convert HSV to RGB color.

        Args:
            h: Hue (0-1).
            s: Saturation (0-1).
            v: Value (0-1).

        Returns:
            RGB color tuple.
        """
        if s == 0:
            r = g = b = int(v * 255)
            return r, g, b

        i = int(h * 6)
        f = (h * 6) - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))

        i %= 6
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        return int(r * 255), int(g * 255), int(b * 255)

    def get_position(self) -> int:
        """Get the current LED position."""
        return self._position

    def set_position(self, position: int) -> None:
        """
        Set the current LED position.

        Args:
            position: LED index position.
        """
        self._position = position % self.led_strip.get_led_count()

    def preview_pace(self, pace_label: str) -> None:
        """
        Display a brief preview of the current pace setting.

        Args:
            pace_label: Human-readable pace label to display concept.
        """
        # Flash the strip to indicate pace change
        original_color = self.primary_color

        for _ in range(2):
            self.led_strip.fill(self.COLOR_WHITE)
            time.sleep(0.1)
            self.led_strip.fill(self.COLOR_OFF)
            time.sleep(0.1)

        self.primary_color = original_color
        logger.info("Pace preview: %s", pace_label)
