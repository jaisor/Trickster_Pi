"""
Unit tests for the config module.
"""

import pytest
from src import config


class TestConfig:
    """Test configuration constants and values."""
    
    def test_gpio_pin_definitions(self):
        """Test that GPIO pin definitions are valid integers."""
        assert isinstance(config.BUTTON_PIN, int)
        assert isinstance(config.SERVO_PIN, int)
        assert isinstance(config.LED_PIN, int)
        
        # Verify pins are in valid GPIO range (0-27 for most Pi models)
        assert 0 <= config.BUTTON_PIN <= 27
        assert 0 <= config.SERVO_PIN <= 27
        assert 0 <= config.LED_PIN <= 27
        
        # Verify pins are unique
        pins = [config.BUTTON_PIN, config.SERVO_PIN, config.LED_PIN]
        assert len(pins) == len(set(pins)), "GPIO pins must be unique"
    
    def test_audio_configuration(self):
        """Test audio configuration values."""
        assert isinstance(config.AUDIO_FOLDER, str)
        assert len(config.AUDIO_FOLDER) > 0
        
        assert isinstance(config.TARGET_AUDIO_DURATION, (int, float))
        assert config.TARGET_AUDIO_DURATION > 0
    
    def test_timing_configuration(self):
        """Test timing configuration values."""
        assert isinstance(config.MIN_DELAY, (int, float))
        assert isinstance(config.MAX_DELAY, (int, float))
        assert config.MIN_DELAY > 0
        assert config.MAX_DELAY > config.MIN_DELAY
        
        assert isinstance(config.MIN_PAUSE_BETWEEN_SOUNDS, (int, float))
        assert isinstance(config.MAX_PAUSE_BETWEEN_SOUNDS, (int, float))
        assert config.MIN_PAUSE_BETWEEN_SOUNDS > 0
        assert config.MAX_PAUSE_BETWEEN_SOUNDS > config.MIN_PAUSE_BETWEEN_SOUNDS
    
    def test_api_configuration(self):
        """Test API configuration values."""
        assert isinstance(config.API_HOST, str)
        assert isinstance(config.API_PORT, int)
        assert isinstance(config.API_DEBUG, bool)
        
        assert 1024 <= config.API_PORT <= 65535  # Valid port range
    
    def test_servo_configuration(self):
        """Test servo configuration values."""
        assert isinstance(config.SERVO_PWM_FREQUENCY, (int, float))
        assert config.SERVO_PWM_FREQUENCY > 0
        
        # Common servo frequencies are typically 50Hz or 60Hz
        assert 20 <= config.SERVO_PWM_FREQUENCY <= 100
    
    def test_configuration_immutability(self):
        """Test that configuration values exist and are accessible."""
        # This test ensures all expected config values are present
        required_configs = [
            'BUTTON_PIN', 'SERVO_PIN', 'LED_PIN',
            'AUDIO_FOLDER', 'TARGET_AUDIO_DURATION',
            'MIN_DELAY', 'MAX_DELAY',
            'MIN_PAUSE_BETWEEN_SOUNDS', 'MAX_PAUSE_BETWEEN_SOUNDS',
            'API_HOST', 'API_PORT', 'API_DEBUG',
            'SERVO_PWM_FREQUENCY'
        ]
        
        for config_name in required_configs:
            assert hasattr(config, config_name), f"Missing configuration: {config_name}"
            assert getattr(config, config_name) is not None, f"Configuration {config_name} is None"
