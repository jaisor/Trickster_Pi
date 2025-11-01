"""
Pytest configuration and shared fixtures for Trickster Pi tests.
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Generator, Dict, Any

# Mock hardware modules that may not be available on development machines
import sys
from unittest.mock import MagicMock

# Mock RPi.GPIO module
mock_gpio = MagicMock()
mock_gpio.BCM = "BCM"
mock_gpio.IN = "IN"
mock_gpio.OUT = "OUT"
mock_gpio.HIGH = 1
mock_gpio.LOW = 0
mock_gpio.PUD_UP = "PUD_UP"
mock_gpio.FALLING = "FALLING"
sys.modules['RPi'] = MagicMock()
sys.modules['RPi.GPIO'] = mock_gpio

# Mock pygame module for audio testing
mock_pygame = MagicMock()
mock_pygame.mixer = MagicMock()
mock_pygame.error = Exception
sys.modules['pygame'] = mock_pygame


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment with mocked hardware."""
    # Ensure pygame mixer is properly mocked
    with patch('pygame.mixer.init'):
        with patch('pygame.mixer.quit'):
            yield


@pytest.fixture
def temp_audio_folder() -> Generator[str, None, None]:
    """Create a temporary directory with sample audio files for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample audio files
        sample_files = [
            "test_sound1.wav",
            "test_sound2.mp3", 
            "test_sound3.WAV",
            "not_audio.txt",  # This should be ignored
            "test_sound4.MP3"
        ]
        
        for filename in sample_files:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"dummy content for {filename}")
        
        yield temp_dir


@pytest.fixture
def mock_gpio_controller():
    """Mock GPIO controller for testing without hardware."""
    with patch('src.gpio_controller.GPIO') as mock_gpio:
        mock_pwm = MagicMock()
        mock_gpio.PWM.return_value = mock_pwm
        
        from src.gpio_controller import GPIOController
        controller = GPIOController()
        controller.servo_pwm = mock_pwm
        
        yield controller, mock_gpio, mock_pwm


@pytest.fixture
def mock_audio_manager():
    """Mock audio manager for testing without pygame."""
    with patch('pygame.mixer.init'):
        with patch('pygame.mixer.Sound') as mock_sound_class:
            mock_sound = MagicMock()
            mock_sound_class.return_value = mock_sound
            
            from src.audio_manager import AudioManager
            manager = AudioManager()
            
            yield manager, mock_sound_class, mock_sound


@pytest.fixture
def sample_audio_info() -> Dict[str, Any]:
    """Sample audio information for testing."""
    return {
        "total_sounds": 3,
        "sounds": ["sound1.wav", "sound2.mp3", "sound3.wav"],
        "audio_folder": "/test/audio"
    }


@pytest.fixture
def flask_test_client():
    """Create a test client for Flask API testing."""
    with patch('src.audio_manager.audio_manager') as mock_audio:
        with patch('src.trickster_controller.trickster_controller') as mock_controller:
            mock_audio.get_audio_info.return_value = {
                "total_sounds": 2,
                "sounds": ["test1.wav", "test2.mp3"],
                "audio_folder": "/test/audio"
            }
            mock_controller.is_busy.return_value = False
            
            from src.api_routes import app
            app.config['TESTING'] = True
            
            with app.test_client() as client:
                yield client, mock_audio, mock_controller


@pytest.fixture
def mock_trickster_controller():
    """Mock trickster controller for testing."""
    with patch('src.audio_manager.audio_manager') as mock_audio:
        with patch('src.gpio_controller.gpio_controller') as mock_gpio:
            from src.trickster_controller import TricksterController
            controller = TricksterController()
            
            yield controller, mock_audio, mock_gpio
