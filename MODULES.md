# Trickster Pi - Module Usage Guide

## Overview

The Trickster Pi project has been refactored into a clean, modular architecture for better maintainability and extensibility.

## Module Responsibilities

### 1. `config.py` - Configuration Management
- **Purpose**: Centralized configuration constants
- **Contains**: GPIO pin definitions, timing settings, API configuration
- **Usage**: Import constants to avoid magic numbers throughout the codebase

```python
from config import BUTTON_PIN, SERVO_PIN, MIN_DELAY
```

### 2. `audio_manager.py` - Audio Operations
- **Purpose**: Audio file loading, preloading, and playback
- **Key Features**:
  - Preloads all audio files at startup for instant playback
  - Supports sequential playback for extended sequences
  - Provides audio information and statistics
- **Usage**: 
```python
from audio_manager import audio_manager
audio_manager.load_audio_files()
audio_manager.play_audio_sequence()
```

### 3. `gpio_controller.py` - Hardware Control
- **Purpose**: GPIO operations for servo, LED, and button
- **Key Features**:
  - Servo angle control and smooth rotation
  - LED state management
  - Button event handling with callbacks
- **Usage**:
```python
from gpio_controller import gpio_controller
gpio_controller.set_led(True)
gpio_controller.rotate_servo()
```

### 4. `trickster_controller.py` - Main Logic
- **Purpose**: Orchestrates the Halloween scare sequence
- **Key Features**:
  - Coordinates audio and servo timing
  - Manages callback state and debouncing
  - Handles the delayed activation sequence
- **Usage**:
```python
from trickster_controller import trickster_controller
trickster_controller.initialize()
```

### 5. `api_routes.py` - REST API
- **Purpose**: HTTP endpoints for remote control
- **Endpoints**:
  - `/play` - Immediate sound playback
  - `/trigger` - Full Halloween sequence
  - `/status` - System information
  - `/sounds` - List audio files
  - `/reload` - Refresh audio files

### 6. `main.py` - Application Entry Point
- **Purpose**: Application startup and coordination
- **Responsibilities**:
  - Initialize all subsystems
  - Start background threads
  - Launch Flask API server
  - Handle graceful shutdown

## Running the Application

### New Modular Version (Recommended)
```bash
python src/main.py
```

### Legacy Version (Single File)
```bash
python src/trickster_legacy.py
```

## Benefits of Modular Architecture

1. **Separation of Concerns**: Each module has a single, clear responsibility
2. **Testability**: Individual components can be tested in isolation  
3. **Maintainability**: Changes to one aspect don't affect others
4. **Reusability**: Modules can be reused in other projects
5. **Readability**: Smaller, focused files are easier to understand
6. **Scalability**: Easy to add new features without cluttering existing code

## Migration Notes

- The original `trickster.py` has been renamed to `trickster_legacy.py`
- All functionality remains identical - just better organized
- Configuration is now centralized and easily modifiable
- The new structure follows Python best practices and design patterns

## Adding New Features

### Adding a New API Endpoint
1. Add the route function to `api_routes.py`
2. Import any needed managers/controllers
3. Return JSON responses using `jsonify()`

### Adding New GPIO Hardware
1. Add pin definitions to `config.py`
2. Add control methods to `gpio_controller.py`
3. Update initialization in `GPIOController.__init__()`

### Modifying Audio Behavior
1. Update parameters in `config.py`
2. Modify methods in `audio_manager.py`
3. No changes needed elsewhere due to encapsulation

This modular architecture makes the Trickster Pi project more professional, maintainable, and ready for future enhancements! 🎃👻
