"""
Unit tests for the trickster_controller module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import time
from src.trickster_controller import TricksterController


class TestTricksterController:
    """Test the TricksterController class."""
    
    def test_init(self):
        """Test TricksterController initialization."""
        controller = TricksterController()
        
        assert controller.callback_in_progress is False
    
    def test_button_callback_when_busy(self, mock_trickster_controller):
        """Test button_callback when another callback is in progress."""
        controller, mock_audio, mock_gpio = mock_trickster_controller
        controller.callback_in_progress = True
        
        with patch('builtins.print') as mock_print:
            controller.button_callback(None)
            
            mock_print.assert_called_with("Button press ignored - action already in progress")
            mock_gpio.set_led.assert_not_called()
            mock_audio.play_audio_sequence.assert_not_called()
    
    @patch('random.uniform')
    @patch('time.sleep')
    @patch('threading.Thread')
    def test_button_callback_success(self, mock_thread, mock_sleep, mock_uniform, 
                                   mock_trickster_controller):
        """Test successful button callback execution."""
        controller, mock_audio, mock_gpio = mock_trickster_controller
        
        # Mock threads
        mock_audio_thread = Mock()
        mock_servo_thread = Mock()
        mock_thread.side_effect = [mock_audio_thread, mock_servo_thread]
        
        # Mock delay
        mock_uniform.return_value = 15.0
        
        with patch('builtins.print') as mock_print:
            controller.button_callback(17)  # Simulate GPIO channel
            
            # Verify LED is turned on
            mock_gpio.set_led.assert_any_call(True)
            
            # Verify delay calculation and sleep
            mock_uniform.assert_called_once()
            mock_sleep.assert_called_once_with(15.0)
            
            # Verify threads are created and started
            assert mock_thread.call_count == 2
            mock_audio_thread.start.assert_called_once()
            mock_servo_thread.start.assert_called_once()
            
            # Verify threads are joined
            mock_audio_thread.join.assert_called_once()
            mock_servo_thread.join.assert_called_once()
            
            # Verify LED is turned off and flag reset
            mock_gpio.set_led.assert_any_call(False)
            assert controller.callback_in_progress is False
    
    @patch('random.uniform')
    @patch('time.sleep')
    @patch('threading.Thread')
    def test_button_callback_exception_handling(self, mock_thread, mock_sleep, mock_uniform, 
                                              mock_trickster_controller):
        """Test button callback with exception in execution."""
        controller, mock_audio, mock_gpio = mock_trickster_controller
        
        # Mock threads
        mock_audio_thread = Mock()
        mock_servo_thread = Mock()
        mock_thread.side_effect = [mock_audio_thread, mock_servo_thread]
        
        # Make sleep raise an exception
        mock_sleep.side_effect = Exception("Test exception")
        mock_uniform.return_value = 15.0
        
        with patch('builtins.print'):
            # Should not raise exception due to try/finally
            controller.button_callback(17)
            
            # Even with exception, LED should be turned off and flag reset
            mock_gpio.set_led.assert_any_call(False)
            assert controller.callback_in_progress is False
    
    def test_is_busy_false(self, mock_trickster_controller):
        """Test is_busy when no callback in progress."""
        controller, mock_audio, mock_gpio = mock_trickster_controller
        controller.callback_in_progress = False
        
        assert controller.is_busy() is False
    
    def test_is_busy_true(self, mock_trickster_controller):
        """Test is_busy when callback in progress."""
        controller, mock_audio, mock_gpio = mock_trickster_controller
        controller.callback_in_progress = True
        
        assert controller.is_busy() is True
    
    def test_initialize(self, mock_trickster_controller):
        """Test initialize method."""
        controller, mock_audio, mock_gpio = mock_trickster_controller
        
        controller.initialize()
        
        # Verify audio files are loaded
        mock_audio.load_audio_files.assert_called_once()
        
        # Verify button callback is registered
        mock_gpio.register_button_callback.assert_called_once_with(controller.button_callback)
    
    def test_start_monitoring(self, mock_trickster_controller):
        """Test start_monitoring method."""
        controller, mock_audio, mock_gpio = mock_trickster_controller
        
        mock_thread = Mock()
        mock_gpio.start_monitoring.return_value = mock_thread
        
        result = controller.start_monitoring()
        
        mock_gpio.start_monitoring.assert_called_once()
        assert result == mock_thread
    
    def test_cleanup(self, mock_trickster_controller):
        """Test cleanup method."""
        controller, mock_audio, mock_gpio = mock_trickster_controller
        
        controller.cleanup()
        
        mock_gpio.cleanup.assert_called_once()
        mock_audio.cleanup.assert_called_once()


class TestTricksterControllerIntegration:
    """Integration tests for TricksterController."""
    
    @pytest.mark.integration
    @patch('random.uniform')
    @patch('time.sleep')
    @patch('threading.Thread')
    def test_full_halloween_sequence(self, mock_thread, mock_sleep, mock_uniform,
                                   mock_trickster_controller):
        """Test a complete Halloween scare sequence."""
        controller, mock_audio, mock_gpio = mock_trickster_controller
        
        # Mock threads with realistic behavior
        mock_audio_thread = Mock()
        mock_servo_thread = Mock()
        mock_thread.side_effect = [mock_audio_thread, mock_servo_thread]
        
        # Mock timing
        mock_uniform.return_value = 12.5
        
        with patch('builtins.print') as mock_print:
            controller.button_callback(17)
            
            # Verify complete sequence
            expected_prints = [
                call("Button pressed!"),
                call("Starting extended audio sequence..."),
                call("Waiting 12.5 seconds before servo activation..."),
                call("Activating servo now!"),
                call("Action completed!")
            ]
            
            mock_print.assert_has_calls(expected_prints)
            
            # Verify timing and threading
            mock_uniform.assert_called_once()
            mock_sleep.assert_called_once_with(12.5)
            
            # Verify both systems activated
            assert mock_thread.call_count == 2
            mock_audio_thread.start.assert_called_once()
            mock_servo_thread.start.assert_called_once()
    
    @pytest.mark.integration
    def test_concurrent_button_presses(self, mock_trickster_controller):
        """Test handling of multiple concurrent button presses."""
        controller, mock_audio, mock_gpio = mock_trickster_controller
        
        # Simulate first button press
        controller.callback_in_progress = True
        
        with patch('builtins.print') as mock_print:
            # Simulate rapid button presses
            controller.button_callback(17)
            controller.button_callback(17)
            controller.button_callback(17)
            
            # All should be ignored
            expected_calls = [
                call("Button press ignored - action already in progress"),
                call("Button press ignored - action already in progress"),
                call("Button press ignored - action already in progress")
            ]
            mock_print.assert_has_calls(expected_calls)
    
    @pytest.mark.integration
    @patch('src.config.MIN_DELAY', 1)
    @patch('src.config.MAX_DELAY', 2)
    @patch('time.sleep')
    @patch('threading.Thread')
    def test_timing_constraints(self, mock_thread, mock_sleep, mock_trickster_controller):
        """Test that timing constraints are respected."""
        controller, mock_audio, mock_gpio = mock_trickster_controller
        
        # Mock threads
        mock_audio_thread = Mock()
        mock_servo_thread = Mock()
        mock_thread.side_effect = [mock_audio_thread, mock_servo_thread]
        
        with patch('builtins.print'):
            controller.button_callback(17)
            
            # Verify sleep was called with a value in the expected range
            mock_sleep.assert_called_once()
            sleep_value = mock_sleep.call_args[0][0]
            assert 1 <= sleep_value <= 2, f"Delay {sleep_value} outside expected range [1, 2]"
