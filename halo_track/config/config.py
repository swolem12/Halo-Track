"""
Configuration management for Halo Track.

Handles loading, saving, and validating configuration from YAML files.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

import yaml


@dataclass
class LEDConfig:
    """Configuration for LED strip hardware."""

    led_count: int = 60
    gpio_pin: int = 18
    brightness: int = 255
    led_freq_hz: int = 800000
    dma_channel: int = 10
    invert: bool = False
    strip_type: str = "WS2812"
    chase_length: int = 5


@dataclass
class KeypadConfig:
    """Configuration for keypad hardware."""

    row_pins: list = field(default_factory=lambda: [17, 27, 22, 5])
    col_pins: list = field(default_factory=lambda: [6, 13, 19, 26])
    debounce_time: float = 0.1


@dataclass
class TrackConfig:
    """Configuration for track parameters."""

    track_length_meters: float = 400.0
    leds_per_meter: float = 30.0


@dataclass
class SafetyConfig:
    """Configuration for safety limits."""

    min_pace_seconds: int = 180
    max_pace_seconds: int = 900
    max_brightness: int = 255
    min_brightness: int = 10
    emergency_stop_enabled: bool = True


@dataclass
class Config:
    """Main configuration container for Halo Track."""

    led: LEDConfig = field(default_factory=LEDConfig)
    keypad: KeypadConfig = field(default_factory=KeypadConfig)
    track: TrackConfig = field(default_factory=TrackConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    default_pace_seconds: int = 480

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "led": {
                "led_count": self.led.led_count,
                "gpio_pin": self.led.gpio_pin,
                "brightness": self.led.brightness,
                "led_freq_hz": self.led.led_freq_hz,
                "dma_channel": self.led.dma_channel,
                "invert": self.led.invert,
                "strip_type": self.led.strip_type,
                "chase_length": self.led.chase_length,
            },
            "keypad": {
                "row_pins": self.keypad.row_pins,
                "col_pins": self.keypad.col_pins,
                "debounce_time": self.keypad.debounce_time,
            },
            "track": {
                "track_length_meters": self.track.track_length_meters,
                "leds_per_meter": self.track.leds_per_meter,
            },
            "safety": {
                "min_pace_seconds": self.safety.min_pace_seconds,
                "max_pace_seconds": self.safety.max_pace_seconds,
                "max_brightness": self.safety.max_brightness,
                "min_brightness": self.safety.min_brightness,
                "emergency_stop_enabled": self.safety.emergency_stop_enabled,
            },
            "default_pace_seconds": self.default_pace_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create configuration from dictionary."""
        led_data = data.get("led", {})
        keypad_data = data.get("keypad", {})
        track_data = data.get("track", {})
        safety_data = data.get("safety", {})

        return cls(
            led=LEDConfig(
                led_count=led_data.get("led_count", 60),
                gpio_pin=led_data.get("gpio_pin", 18),
                brightness=led_data.get("brightness", 255),
                led_freq_hz=led_data.get("led_freq_hz", 800000),
                dma_channel=led_data.get("dma_channel", 10),
                invert=led_data.get("invert", False),
                strip_type=led_data.get("strip_type", "WS2812"),
                chase_length=led_data.get("chase_length", 5),
            ),
            keypad=KeypadConfig(
                row_pins=keypad_data.get("row_pins", [17, 27, 22, 5]),
                col_pins=keypad_data.get("col_pins", [6, 13, 19, 26]),
                debounce_time=keypad_data.get("debounce_time", 0.1),
            ),
            track=TrackConfig(
                track_length_meters=track_data.get("track_length_meters", 400.0),
                leds_per_meter=track_data.get("leds_per_meter", 30.0),
            ),
            safety=SafetyConfig(
                min_pace_seconds=safety_data.get("min_pace_seconds", 180),
                max_pace_seconds=safety_data.get("max_pace_seconds", 900),
                max_brightness=safety_data.get("max_brightness", 255),
                min_brightness=safety_data.get("min_brightness", 10),
                emergency_stop_enabled=safety_data.get("emergency_stop_enabled", True),
            ),
            default_pace_seconds=data.get("default_pace_seconds", 480),
        )


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the configuration file. If None, uses default config.

    Returns:
        Config object with loaded settings.
    """
    if config_path is None:
        config_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(config_dir, "default_config.yaml")

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data:
                return Config.from_dict(data)

    return Config()


def save_config(config: Config, config_path: str) -> None:
    """
    Save configuration to a YAML file.

    Args:
        config: Config object to save.
        config_path: Path to save the configuration file.
    """
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False)
