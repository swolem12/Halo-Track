#!/usr/bin/env python3
"""
Halo Track - Main Application Entry Point

Augmented running aid using LED pacing on Raspberry Pi 4.
"""

import argparse
import logging
import signal
import sys
import time
from typing import Optional

from halo_track.config import Config, load_config
from halo_track.devices import LEDStrip, Keypad
from halo_track.devices.keypad import PaceInputHandler
from halo_track.engine import TimingEngine, PacingLogic
from halo_track.engine.pacing_logic import PacingMode
from halo_track.safety import SafetyLimits

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("halo_track")


class HaloTrackApp:
    """
    Main application class for Halo Track.

    Coordinates LED pacing, keypad input, and timing for the
    augmented running aid system.
    """

    def __init__(self, config: Config, simulation_mode: bool = False):
        """
        Initialize the Halo Track application.

        Args:
            config: Configuration object.
            simulation_mode: Run in simulation mode without hardware.
        """
        self.config = config
        self.simulation_mode = simulation_mode
        self._running = False

        # Initialize components
        self.led_strip = LEDStrip(
            led_count=config.led.led_count,
            gpio_pin=config.led.gpio_pin,
            brightness=config.led.brightness,
            led_freq_hz=config.led.led_freq_hz,
            dma_channel=config.led.dma_channel,
            invert=config.led.invert,
            simulation_mode=simulation_mode,
        )

        self.keypad = Keypad(
            row_pins=config.keypad.row_pins,
            col_pins=config.keypad.col_pins,
            debounce_time=config.keypad.debounce_time,
            simulation_mode=simulation_mode,
        )

        self.timing_engine = TimingEngine(
            track_length_meters=config.track.track_length_meters,
            led_count=config.led.led_count,
            leds_per_meter=config.track.leds_per_meter,
        )

        self.pacing_logic = PacingLogic(
            led_strip=self.led_strip,
            chase_length=config.led.chase_length,
        )

        self.safety_limits = SafetyLimits(
            min_pace_seconds=config.safety.min_pace_seconds,
            max_pace_seconds=config.safety.max_pace_seconds,
            max_brightness=config.safety.max_brightness,
            min_brightness=config.safety.min_brightness,
            emergency_stop_enabled=config.safety.emergency_stop_enabled,
        )

        self.pace_input = PaceInputHandler(self.keypad)

        # Current state
        self.current_pace_seconds = config.default_pace_seconds
        self._start_time: Optional[float] = None

        logger.info("Halo Track application initialized")

    def initialize(self) -> bool:
        """
        Initialize all hardware components.

        Returns:
            True if initialization was successful.
        """
        logger.info("Initializing hardware...")

        if not self.led_strip.initialize():
            logger.error("Failed to initialize LED strip")
            return False

        if not self.keypad.initialize():
            logger.error("Failed to initialize keypad")
            return False

        logger.info("Hardware initialization complete")
        return True

    def cleanup(self) -> None:
        """Clean up all resources."""
        logger.info("Cleaning up resources...")
        self.pacing_logic.stop()
        self.led_strip.cleanup()
        self.keypad.cleanup()
        logger.info("Cleanup complete")

    def set_pace(self, pace_seconds: int) -> bool:
        """
        Set the target running pace.

        Args:
            pace_seconds: Pace in seconds per kilometer.

        Returns:
            True if pace was set successfully.
        """
        # Validate pace against safety limits
        is_valid, clamped_pace, message = self.safety_limits.validate_pace(pace_seconds)

        if not is_valid:
            logger.warning(message)
            pace_seconds = clamped_pace

        self.current_pace_seconds = pace_seconds

        # Update timing
        timing = self.timing_engine.calculate_timing(pace_seconds)
        self.pacing_logic.set_led_interval(timing.led_interval_ms)

        pace_str = self.timing_engine.format_pace(pace_seconds)
        logger.info("Pace set to: %s (%.2f m/s)", pace_str, timing.meters_per_second)

        return True

    def start_pacing(self) -> None:
        """Start the pacing animation."""
        if self.safety_limits.is_emergency_stop_active():
            logger.warning("Cannot start - emergency stop is active")
            return

        self._start_time = time.time()
        self.pacing_logic.start()
        logger.info("Pacing started at %s", self.timing_engine.format_pace(self.current_pace_seconds))

    def stop_pacing(self) -> None:
        """Stop the pacing animation."""
        self.pacing_logic.stop()
        elapsed = time.time() - self._start_time if self._start_time else 0
        logger.info("Pacing stopped after %s", self.timing_engine.format_time(elapsed))

    def handle_keypad_input(self) -> None:
        """Process keypad input."""
        key = self.keypad.poll()

        if key is None:
            return

        logger.debug("Key pressed: %s", key)

        # Handle special keys
        if key == "A":
            # Start/Resume pacing
            if not self.pacing_logic.is_running():
                self.start_pacing()
            return

        if key == "B":
            # Stop pacing
            self.stop_pacing()
            return

        if key == "C":
            # Change mode
            current_mode = self.pacing_logic.get_mode()
            modes = list(PacingMode)
            current_idx = modes.index(current_mode)
            next_idx = (current_idx + 1) % len(modes)
            self.pacing_logic.set_mode(modes[next_idx])
            return

        if key == "D":
            # Emergency stop
            self.emergency_stop()
            return

        # Process numeric input for pace
        result = self.pace_input.process_key(key)
        if result is not None:
            self.set_pace(result)
            self.pacing_logic.preview_pace(
                self.timing_engine.format_pace(result)
            )

    def emergency_stop(self) -> None:
        """Trigger emergency stop."""
        self.safety_limits.trigger_emergency_stop()
        self.pacing_logic.stop()
        self.led_strip.clear()
        logger.warning("EMERGENCY STOP ACTIVATED")

    def reset_emergency_stop(self) -> None:
        """Reset emergency stop."""
        self.safety_limits.reset_emergency_stop()
        logger.info("Emergency stop reset")

    def run(self) -> None:
        """Main application loop."""
        self._running = True
        logger.info("Halo Track running. Press Ctrl+C to exit.")

        # Set initial pace
        self.set_pace(self.current_pace_seconds)

        try:
            while self._running:
                # Handle keypad input
                self.handle_keypad_input()

                # Update LED display
                self.pacing_logic.update()

                # Small sleep to prevent CPU hogging
                time.sleep(0.001)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")

        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the application."""
        self._running = False
        self.cleanup()

    def get_status(self) -> dict:
        """
        Get current application status.

        Returns:
            Dictionary with status information.
        """
        elapsed = 0
        if self._start_time and self.pacing_logic.is_running():
            elapsed = time.time() - self._start_time

        laps, progress = self.timing_engine.get_lap_count_at_time(
            elapsed, self.current_pace_seconds
        )

        return {
            "running": self.pacing_logic.is_running(),
            "pace": self.timing_engine.format_pace(self.current_pace_seconds),
            "pace_seconds": self.current_pace_seconds,
            "mode": self.pacing_logic.get_mode().value,
            "elapsed_time": self.timing_engine.format_time(elapsed),
            "laps_completed": laps,
            "lap_progress": progress,
            "emergency_stop": self.safety_limits.is_emergency_stop_active(),
            "simulation_mode": self.simulation_mode,
        }


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("Signal %s received, shutting down...", signum)
    sys.exit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Halo Track - Augmented Running Aid",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Run with default configuration
  %(prog)s --config my.yaml   Run with custom configuration
  %(prog)s --simulate         Run in simulation mode (no hardware)
  %(prog)s --pace 7:30        Start with 7:30 min/km pace
        """,
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (YAML)",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run in simulation mode without hardware",
    )
    parser.add_argument(
        "--pace",
        type=str,
        help="Initial pace (format: M:SS or MM:SS)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Halo Track 1.0.0",
    )

    args = parser.parse_args()

    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Load configuration
    config = load_config(args.config)

    # Create application
    app = HaloTrackApp(config, simulation_mode=args.simulate)

    # Initialize hardware
    if not app.initialize():
        logger.error("Failed to initialize hardware")
        sys.exit(1)

    # Set initial pace if provided
    if args.pace:
        from halo_track.utils import pace_to_seconds

        try:
            pace_seconds = pace_to_seconds(args.pace)
            app.set_pace(pace_seconds)
        except ValueError as e:
            logger.error("Invalid pace format: %s", e)
            sys.exit(1)

    # Run application
    try:
        app.run()
    except Exception as e:
        logger.exception("Application error: %s", e)
        app.cleanup()
        sys.exit(1)

    logger.info("Halo Track shutdown complete")


if __name__ == "__main__":
    main()
