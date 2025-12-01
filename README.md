# Halo Track

Augmented running aid using LED pacing on Raspberry Pi 4.

## Overview

Halo Track is a Python application designed for the Raspberry Pi 4 that provides visual pacing guidance for runners using WS2812B LED strips. The system displays a "chase" pattern on the LED strip that moves at a speed corresponding to the target running pace, helping runners maintain consistent speed during training.

## Features

- **LED Pacing**: WS2812B LED strip control with chase patterns
- **Keypad Input**: 4x4 matrix keypad for pace selection
- **Timing Engine**: Converts running pace to LED chase speed
- **Safety Limits**: Configurable pace and brightness limits
- **Modular Design**: Easy to extend with future features
- **Simulation Mode**: Test without hardware

## Hardware Requirements

- Raspberry Pi 4
- WS2812B LED strip (addressable RGB LEDs)
- 4x4 Matrix keypad
- 5V power supply (adequate for LED count)
- Level shifter (recommended for data signal)

## Wiring

### LED Strip (WS2812B)
| LED Strip | Raspberry Pi |
|-----------|--------------|
| VCC (5V)  | 5V or external supply |
| GND       | Ground |
| DIN       | GPIO 18 (PWM) |

### Keypad (4x4 Matrix)
| Keypad    | Raspberry Pi GPIO |
|-----------|-------------------|
| Row 1     | GPIO 17 |
| Row 2     | GPIO 27 |
| Row 3     | GPIO 22 |
| Row 4     | GPIO 5 |
| Col 1     | GPIO 6 |
| Col 2     | GPIO 13 |
| Col 3     | GPIO 19 |
| Col 4     | GPIO 26 |

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/swolem12/Halo-Track.git
cd Halo-Track
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# On Raspberry Pi, install hardware libraries
sudo pip install rpi_ws281x RPi.GPIO
```

### 3. Configure the System

Edit `halo_track/config/default_config.yaml` to match your setup:

```yaml
led:
  led_count: 60          # Number of LEDs in your strip
  gpio_pin: 18           # GPIO pin for data
  brightness: 255        # Default brightness (0-255)

track:
  track_length_meters: 400.0  # Length of your track
```

## Usage

### Running the Application

```bash
# Run with default settings
sudo python -m halo_track.main

# Run in simulation mode (no hardware required)
python -m halo_track.main --simulate

# Run with custom configuration
sudo python -m halo_track.main --config my_config.yaml

# Start with specific pace (7:30 min/km)
sudo python -m halo_track.main --pace 7:30

# Enable debug logging
sudo python -m halo_track.main --debug
```

**Note**: Root access (`sudo`) is required for GPIO access on Raspberry Pi.

### Keypad Controls

| Key | Function |
|-----|----------|
| 0-9 | Enter pace (format: MMSS, e.g., 0800 = 8:00) |
| # | Confirm pace input |
| * | Clear pace input |
| A | Start/Resume pacing |
| B | Stop pacing |
| C | Change display mode |
| D | Emergency stop |

### Entering a Pace

1. Enter the pace in MMSS format (e.g., `0730` for 7:30 min/km)
2. Press `#` to confirm
3. Press `A` to start the pacing animation

## Project Structure

```
halo_track/
├── __init__.py           # Package initialization
├── main.py               # Main application entry point
├── config/
│   ├── __init__.py
│   ├── config.py         # Configuration management
│   └── default_config.yaml  # Default settings
├── devices/
│   ├── __init__.py
│   ├── led_strip.py      # WS2812B LED control
│   └── keypad.py         # Keypad input handling
├── engine/
│   ├── __init__.py
│   ├── timing_engine.py  # Pace to LED speed conversion
│   └── pacing_logic.py   # LED chase patterns
├── safety/
│   ├── __init__.py
│   └── limits.py         # Safety limits and validation
└── utils/
    ├── __init__.py
    └── helpers.py        # Utility functions
```

## Configuration

The configuration file (`default_config.yaml`) supports the following settings:

### LED Configuration
- `led_count`: Number of LEDs in the strip
- `gpio_pin`: GPIO pin for data signal
- `brightness`: Default brightness (0-255)
- `chase_length`: Number of LEDs in chase pattern

### Track Configuration
- `track_length_meters`: Length of the running track
- `leds_per_meter`: LED density per meter

### Safety Limits
- `min_pace_seconds`: Minimum pace (fastest)
- `max_pace_seconds`: Maximum pace (slowest)
- `max_brightness`: Maximum LED brightness
- `emergency_stop_enabled`: Enable emergency stop

## Extending the System

The modular architecture makes it easy to add new features:

1. **New Display Modes**: Add new patterns in `pacing_logic.py`
2. **Additional Sensors**: Create new device classes in `devices/`
3. **Network Control**: Add API endpoints using Flask or FastAPI
4. **Data Logging**: Add workout recording in a new module

## Troubleshooting

### Common Issues

1. **LEDs not lighting up**
   - Check power supply (5V, adequate current)
   - Verify GPIO pin connection
   - Run with `sudo` for GPIO access

2. **Keypad not responding**
   - Check GPIO pin connections
   - Verify debounce time in config
   - Run with `--debug` for diagnostics

3. **Import errors**
   - Use `--simulate` mode to test without hardware
   - Install Raspberry Pi libraries with `sudo pip install`

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests.
