"""
Hardware-specific tests for Raspberry Pi GPIO functionality.
These tests should only be run on actual Raspberry Pi hardware.
"""

import pytest
import time
import os
from unittest.mock import patch


@pytest.mark.hardware
class TestHardwareGPIO:
    """Hardware tests that require actual Raspberry Pi GPIO."""
    
    def test_gpio_availability(self):
        """Test that GPIO hardware is available."""
        # Skip if not on Raspberry Pi
        if not self._is_raspberry_pi():
            pytest.skip("Not running on Raspberry Pi hardware")
        
        try:
            import RPi.GPIO as GPIO
            # Basic GPIO test - should not raise exception
            GPIO.setmode(GPIO.BCM)
            GPIO.cleanup()
        except Exception as e:
            pytest.fail(f"GPIO hardware not accessible: {e}")
    
    def test_servo_pwm_hardware(self):
        """Test actual servo PWM functionality."""
        if not self._is_raspberry_pi():
            pytest.skip("Not running on Raspberry Pi hardware")
        
        try:
            from src.gpio_controller import GPIOController
            controller = GPIOController()
            
            # Test servo movement (brief test)
            controller.set_servo_angle(0)
            time.sleep(0.1)
            controller.set_servo_angle(90)
            time.sleep(0.1)
            controller.set_servo_angle(180)
            time.sleep(0.1)
            
            controller.cleanup()
            
        except Exception as e:
            pytest.fail(f"Servo PWM hardware test failed: {e}")
    
    def test_led_hardware(self):
        """Test actual LED control."""
        if not self._is_raspberry_pi():
            pytest.skip("Not running on Raspberry Pi hardware")
        
        try:
            from src.gpio_controller import GPIOController
            controller = GPIOController()
            
            # Test LED on/off
            controller.set_led(True)
            time.sleep(0.1)
            controller.set_led(False)
            time.sleep(0.1)
            
            controller.cleanup()
            
        except Exception as e:
            pytest.fail(f"LED hardware test failed: {e}")
    
    def _is_raspberry_pi(self) -> bool:
        """Check if running on Raspberry Pi."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'BCM' in cpuinfo or 'raspberry' in cpuinfo.lower()
        except FileNotFoundError:
            return False


@pytest.mark.hardware
class TestHardwareAudio:
    """Hardware tests for audio functionality."""
    
    def test_pygame_audio_hardware(self):
        """Test pygame audio system on hardware."""
        if not self._has_audio_hardware():
            pytest.skip("No audio hardware detected")
        
        try:
            import pygame
            pygame.mixer.init()
            
            # Test basic mixer functionality
            assert pygame.mixer.get_init() is not None
            
            pygame.mixer.quit()
            
        except Exception as e:
            pytest.fail(f"Audio hardware test failed: {e}")
    
    def test_audio_file_playback(self):
        """Test actual audio file playback."""
        if not self._has_audio_hardware():
            pytest.skip("No audio hardware detected")
        
        # Create a test audio file (silence)
        test_audio_file = "/tmp/test_silence.wav"
        self._create_test_wav_file(test_audio_file)
        
        try:
            from src.audio_manager import AudioManager
            
            # Temporarily patch AUDIO_FOLDER to use test file
            with patch('src.audio_manager.AUDIO_FOLDER', '/tmp'):
                manager = AudioManager()
                manager.load_audio_files()
                
                if manager.preloaded_sounds:
                    result = manager.play_random_sound()
                    assert result["success"] is True
                else:
                    pytest.skip("No test audio files loaded")
                
                manager.cleanup()
                
        except Exception as e:
            pytest.fail(f"Audio playback test failed: {e}")
        finally:
            # Clean up test file
            if os.path.exists(test_audio_file):
                os.remove(test_audio_file)
    
    def _has_audio_hardware(self) -> bool:
        """Check if audio hardware is available."""
        try:
            import pygame
            pygame.mixer.init()
            has_audio = pygame.mixer.get_init() is not None
            pygame.mixer.quit()
            return has_audio
        except:
            return False
    
    def _create_test_wav_file(self, filename: str):
        """Create a minimal WAV file for testing."""
        # Create a minimal WAV file (1 second of silence)
        import wave
        import struct
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(44100)  # 44.1kHz
            
            # 1 second of silence
            for i in range(44100):
                wav_file.writeframes(struct.pack('<h', 0))


@pytest.mark.hardware
class TestHardwareIntegration:
    """Integration tests requiring full hardware setup."""
    
    def test_full_system_hardware(self):
        """Test complete system integration on hardware."""
        if not self._is_raspberry_pi():
            pytest.skip("Not running on Raspberry Pi hardware")
        
        try:
            from src.trickster_controller import TricksterController
            
            controller = TricksterController()
            controller.initialize()
            
            # Verify system is ready
            assert not controller.is_busy()
            
            # Test a quick sequence (with short delays for testing)
            with patch('src.config.MIN_DELAY', 0.1):
                with patch('src.config.MAX_DELAY', 0.2):
                    with patch('src.config.TARGET_AUDIO_DURATION', 1):
                        
                        # Simulate button press
                        controller.button_callback(None)
                        
                        # Wait for sequence to complete
                        time.sleep(2)
                        
                        # System should be ready again
                        assert not controller.is_busy()
            
            controller.cleanup()
            
        except Exception as e:
            pytest.fail(f"Full system hardware test failed: {e}")
    
    def test_concurrent_hardware_operations(self):
        """Test concurrent GPIO and audio operations."""
        if not self._is_raspberry_pi():
            pytest.skip("Not running on Raspberry Pi hardware")
        
        try:
            from src.gpio_controller import GPIOController
            from src.audio_manager import AudioManager
            import threading
            
            gpio_controller = GPIOController()
            audio_manager = AudioManager()
            
            # Test concurrent operations
            def gpio_operations():
                for _ in range(5):
                    gpio_controller.set_led(True)
                    time.sleep(0.1)
                    gpio_controller.set_led(False)
                    time.sleep(0.1)
            
            def audio_operations():
                # Only if audio files are available
                if audio_manager.preloaded_sounds:
                    audio_manager.play_random_sound()
            
            # Run operations concurrently
            gpio_thread = threading.Thread(target=gpio_operations)
            audio_thread = threading.Thread(target=audio_operations)
            
            gpio_thread.start()
            audio_thread.start()
            
            gpio_thread.join(timeout=5)
            audio_thread.join(timeout=5)
            
            gpio_controller.cleanup()
            audio_manager.cleanup()
            
        except Exception as e:
            pytest.fail(f"Concurrent hardware operations test failed: {e}")
    
    def _is_raspberry_pi(self) -> bool:
        """Check if running on Raspberry Pi."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'BCM' in cpuinfo or 'raspberry' in cpuinfo.lower()
        except FileNotFoundError:
            return False
