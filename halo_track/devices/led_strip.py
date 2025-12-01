"""
WS2812B LED Strip Controller for Halo Track.

Provides hardware abstraction for controlling WS2812B LED strips
on Raspberry Pi using the rpi_ws281x library.
"""

import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class LEDStrip:
    """
    Controller for WS2812B LED strip hardware.

    Provides methods for initializing, controlling, and displaying
    patterns on LED strips connected to the Raspberry Pi GPIO.
    """

    # RGB color encoding bit shifts for 24-bit color
    RED_SHIFT = 16
    GREEN_SHIFT = 8
    BLUE_MASK = 0xFF

    def __init__(
        self,
        led_count: int = 60,
        gpio_pin: int = 18,
        brightness: int = 255,
        led_freq_hz: int = 800000,
        dma_channel: int = 10,
        invert: bool = False,
        simulation_mode: bool = False,
    ):
        """
        Initialize the LED strip controller.

        Args:
            led_count: Number of LEDs in the strip.
            gpio_pin: GPIO pin number for data signal.
            brightness: Default brightness (0-255).
            led_freq_hz: LED signal frequency in Hz.
            dma_channel: DMA channel for PWM.
            invert: Invert signal for level shifters.
            simulation_mode: If True, simulate LED behavior without hardware.
        """
        self.led_count = led_count
        self.gpio_pin = gpio_pin
        self.brightness = brightness
        self.led_freq_hz = led_freq_hz
        self.dma_channel = dma_channel
        self.invert = invert
        self.simulation_mode = simulation_mode
        self._strip = None
        self._initialized = False

        # Virtual LED buffer for simulation mode
        self._virtual_leds = [(0, 0, 0)] * led_count

    def initialize(self) -> bool:
        """
        Initialize the LED strip hardware.

        Returns:
            True if initialization was successful, False otherwise.
        """
        if self.simulation_mode:
            logger.info(
                "LED strip initialized in simulation mode with %d LEDs",
                self.led_count,
            )
            self._initialized = True
            return True

        try:
            # Import rpi_ws281x only when not in simulation mode
            from rpi_ws281x import PixelStrip, ws

            strip_type = ws.WS2811_STRIP_GRB

            self._strip = PixelStrip(
                self.led_count,
                self.gpio_pin,
                self.led_freq_hz,
                self.dma_channel,
                self.invert,
                self.brightness,
                0,
                strip_type,
            )
            self._strip.begin()
            self._initialized = True
            logger.info("LED strip initialized with %d LEDs", self.led_count)
            return True

        except ImportError:
            logger.warning(
                "rpi_ws281x not available, switching to simulation mode"
            )
            self.simulation_mode = True
            self._initialized = True
            return True

        except Exception as e:
            logger.error("Failed to initialize LED strip: %s", e)
            return False

    def cleanup(self) -> None:
        """Clean up LED strip resources."""
        if self._initialized:
            self.clear()
            self._initialized = False
            logger.info("LED strip cleaned up")

    def set_pixel(
        self, index: int, color: Tuple[int, int, int]
    ) -> bool:
        """
        Set a single pixel to a specific color.

        Args:
            index: LED index (0 to led_count - 1).
            color: RGB color tuple (red, green, blue) with values 0-255.

        Returns:
            True if successful, False otherwise.
        """
        if not self._initialized:
            logger.warning("LED strip not initialized")
            return False

        if not 0 <= index < self.led_count:
            logger.warning("LED index %d out of range", index)
            return False

        r, g, b = color
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        if self.simulation_mode:
            self._virtual_leds[index] = (r, g, b)
        else:
            # Convert RGB to 24-bit color value
            color_value = (r << self.RED_SHIFT) | (g << self.GREEN_SHIFT) | b
            self._strip.setPixelColor(index, color_value)

        return True

    def get_pixel(self, index: int) -> Optional[Tuple[int, int, int]]:
        """
        Get the current color of a pixel.

        Args:
            index: LED index (0 to led_count - 1).

        Returns:
            RGB color tuple or None if invalid index.
        """
        if not 0 <= index < self.led_count:
            return None

        if self.simulation_mode:
            return self._virtual_leds[index]
        elif self._strip:
            color = self._strip.getPixelColor(index)
            return (
                (color >> self.RED_SHIFT) & self.BLUE_MASK,
                (color >> self.GREEN_SHIFT) & self.BLUE_MASK,
                color & self.BLUE_MASK,
            )

        return None

    def fill(self, color: Tuple[int, int, int]) -> None:
        """
        Fill all LEDs with a single color.

        Args:
            color: RGB color tuple (red, green, blue).
        """
        for i in range(self.led_count):
            self.set_pixel(i, color)
        self.show()

    def clear(self) -> None:
        """Turn off all LEDs."""
        self.fill((0, 0, 0))

    def show(self) -> None:
        """Update the LED strip with the current pixel values."""
        if not self._initialized:
            return

        if self.simulation_mode:
            # In simulation mode, optionally log the state
            logger.debug("LED strip updated (simulation mode)")
        else:
            self._strip.show()

    def set_brightness(self, brightness: int) -> None:
        """
        Set the overall strip brightness.

        Args:
            brightness: Brightness value (0-255).
        """
        self.brightness = max(0, min(255, brightness))

        if not self.simulation_mode and self._strip:
            self._strip.setBrightness(self.brightness)

        logger.debug("LED brightness set to %d", self.brightness)

    def get_led_count(self) -> int:
        """Get the number of LEDs in the strip."""
        return self.led_count

    def is_initialized(self) -> bool:
        """Check if the LED strip is initialized."""
        return self._initialized

    def get_virtual_state(self) -> list:
        """
        Get the virtual LED state (for testing/simulation).

        Returns:
            List of RGB tuples representing LED colors.
        """
        if self.simulation_mode:
            return self._virtual_leds.copy()
        return []
