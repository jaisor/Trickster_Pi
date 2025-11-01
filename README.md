# Trickster Pi 🎃👻

A sophisticated Raspberry Pi-based Halloween automation system that creates immersive scare experiences with synchronized audio and servo motor control, plus REST API for remote management.

## Features

- **Random Audio Sequences**: Plays multiple spooky sounds for 60+ seconds
- **Delayed Servo Action**: 10-20 second random delay before servo activation
- **Smart Debouncing**: Ignores button presses while action is in progress
- **REST API**: Remote control via HTTP endpoints
- **Modular Architecture**: Clean, organized code structure
- **Real-time Audio Loading**: Hot-reload audio files without restart

## Project Structure

```
src/
├── __init__.py              # Package initialization
├── main.py                  # Application entry point
├── config.py                # Configuration constants
├── audio_manager.py         # Audio loading and playback
├── gpio_controller.py       # GPIO operations (servo, LED, button)
├── trickster_controller.py  # Main orchestration logic
├── api_routes.py           # REST API endpoints
└── trickster.py            # Legacy monolithic file (deprecated)
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

## API Endpoints

- `GET /play` - Play a random sound (immediate)
- `GET /trigger` - Trigger delayed Halloween sequence
- `GET /status` - Get system status
- `GET /sounds` - List available audio files
- `GET /reload` - Reload audio files from folder

## Hardware Requirements

- Raspberry Pi (any model with GPIO)
- Servo motor connected to GPIO pin 12
- Button connected to GPIO pin 17
- LED connected to GPIO pin 16
- Audio files (.wav or .mp3) in configured folder
