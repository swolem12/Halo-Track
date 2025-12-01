"""
Keypad Input Handler for Halo Track.

Provides hardware abstraction for 4x4 matrix keypads
connected to Raspberry Pi GPIO pins.
"""

import logging
import time
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class Keypad:
    """
    Controller for 4x4 matrix keypad hardware.

    Provides methods for reading key presses from a matrix keypad
    connected to the Raspberry Pi GPIO.
    """

    # Standard 4x4 keypad layout
    KEYMAP = [
        ["1", "2", "3", "A"],
        ["4", "5", "6", "B"],
        ["7", "8", "9", "C"],
        ["*", "0", "#", "D"],
    ]

    def __init__(
        self,
        row_pins: list = None,
        col_pins: list = None,
        debounce_time: float = 0.1,
        simulation_mode: bool = False,
    ):
        """
        Initialize the keypad controller.

        Args:
            row_pins: List of GPIO pin numbers for rows.
            col_pins: List of GPIO pin numbers for columns.
            debounce_time: Debounce time in seconds.
            simulation_mode: If True, simulate keypad without hardware.
        """
        self.row_pins = row_pins or [17, 27, 22, 5]
        self.col_pins = col_pins or [6, 13, 19, 26]
        self.debounce_time = debounce_time
        self.simulation_mode = simulation_mode
        self._initialized = False
        self._last_key_time = 0
        self._last_key = None
        self._callback: Optional[Callable[[str], None]] = None

        # Simulated key press queue
        self._simulated_keys = []

    def initialize(self) -> bool:
        """
        Initialize the keypad hardware.

        Returns:
            True if initialization was successful, False otherwise.
        """
        if self.simulation_mode:
            logger.info("Keypad initialized in simulation mode")
            self._initialized = True
            return True

        try:
            # Import GPIO only when not in simulation mode
            import RPi.GPIO as GPIO

            GPIO.setmode(GPIO.BCM)

            # Set up row pins as outputs
            for pin in self.row_pins:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.HIGH)

            # Set up column pins as inputs with pull-up resistors
            for pin in self.col_pins:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            self._initialized = True
            logger.info("Keypad initialized")
            return True

        except ImportError:
            logger.warning("RPi.GPIO not available, switching to simulation mode")
            self.simulation_mode = True
            self._initialized = True
            return True

        except Exception as e:
            logger.error("Failed to initialize keypad: %s", e)
            return False

    def cleanup(self) -> None:
        """Clean up keypad resources."""
        if self._initialized and not self.simulation_mode:
            try:
                import RPi.GPIO as GPIO

                for pin in self.row_pins + self.col_pins:
                    GPIO.cleanup(pin)
            except ImportError:
                pass

        self._initialized = False
        logger.info("Keypad cleaned up")

    def read_key(self) -> Optional[str]:
        """
        Read a single key press from the keypad.

        Returns:
            The key character pressed, or None if no key is pressed.
        """
        if not self._initialized:
            logger.warning("Keypad not initialized")
            return None

        current_time = time.time()

        # Check debounce
        if current_time - self._last_key_time < self.debounce_time:
            return None

        if self.simulation_mode:
            if self._simulated_keys:
                key = self._simulated_keys.pop(0)
                self._last_key_time = current_time
                self._last_key = key
                return key
            return None

        try:
            import RPi.GPIO as GPIO

            for row_idx, row_pin in enumerate(self.row_pins):
                # Set current row LOW
                GPIO.output(row_pin, GPIO.LOW)

                for col_idx, col_pin in enumerate(self.col_pins):
                    if GPIO.input(col_pin) == GPIO.LOW:
                        # Key is pressed
                        key = self.KEYMAP[row_idx][col_idx]

                        # Wait for key release
                        while GPIO.input(col_pin) == GPIO.LOW:
                            time.sleep(0.01)

                        # Reset row
                        GPIO.output(row_pin, GPIO.HIGH)

                        self._last_key_time = current_time
                        self._last_key = key
                        return key

                # Reset row
                GPIO.output(row_pin, GPIO.HIGH)

            return None

        except Exception as e:
            logger.error("Error reading keypad: %s", e)
            return None

    def simulate_key_press(self, key: str) -> None:
        """
        Simulate a key press (for testing).

        Args:
            key: The key character to simulate.
        """
        if self.simulation_mode:
            self._simulated_keys.append(key)

    def set_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set a callback function to be called when a key is pressed.

        Args:
            callback: Function to call with the key character.
        """
        self._callback = callback

    def poll(self) -> Optional[str]:
        """
        Poll for a key press and call the callback if set.

        Returns:
            The key pressed, or None if no key is pressed.
        """
        key = self.read_key()
        if key and self._callback:
            self._callback(key)
        return key

    def get_last_key(self) -> Optional[str]:
        """Get the last key that was pressed."""
        return self._last_key

    def is_initialized(self) -> bool:
        """Check if the keypad is initialized."""
        return self._initialized


class PaceInputHandler:
    """
    Handles pace input from the keypad.

    Provides methods for entering and validating running pace values.
    """

    # Constants for pace input parsing
    PACE_INPUT_LENGTH = 4
    MINUTES_END_INDEX = 2
    SECONDS_START_INDEX = 2
    MAX_SECONDS = 60

    def __init__(self, keypad: Keypad):
        """
        Initialize the pace input handler.

        Args:
            keypad: Keypad instance for input.
        """
        self.keypad = keypad
        self._input_buffer = ""
        self._input_complete = False

    def process_key(self, key: str) -> Optional[int]:
        """
        Process a key press for pace input.

        Format: MMSS (minutes:seconds) - e.g., 0800 for 8:00 min/km

        Args:
            key: The key character pressed.

        Returns:
            Pace in seconds if input is complete, None otherwise.
        """
        if key == "#":
            # Confirm input
            if len(self._input_buffer) >= 3:
                pace_seconds = self._parse_pace()
                self._input_buffer = ""
                self._input_complete = True
                return pace_seconds
            return None

        elif key == "*":
            # Clear input
            self._input_buffer = ""
            self._input_complete = False
            return None

        elif key.isdigit():
            # Add digit to buffer (max PACE_INPUT_LENGTH digits)
            if len(self._input_buffer) < self.PACE_INPUT_LENGTH:
                self._input_buffer += key
            return None

        return None

    def _parse_pace(self) -> Optional[int]:
        """
        Parse the input buffer as a pace value.

        Returns:
            Pace in seconds, or None if invalid.
        """
        try:
            # Pad with leading zeros if needed
            pace_str = self._input_buffer.zfill(self.PACE_INPUT_LENGTH)
            minutes = int(pace_str[:self.MINUTES_END_INDEX])
            seconds = int(pace_str[self.SECONDS_START_INDEX:])

            if 0 <= seconds < self.MAX_SECONDS:
                return minutes * 60 + seconds
            return None

        except ValueError:
            return None

    def get_current_input(self) -> str:
        """Get the current input buffer contents."""
        return self._input_buffer

    def clear_input(self) -> None:
        """Clear the input buffer."""
        self._input_buffer = ""
        self._input_complete = False

    def is_input_complete(self) -> bool:
        """Check if input is complete."""
        return self._input_complete
