"""
Unit tests for the gpio_controller module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from src.gpio_controller import GPIOController


class TestGPIOController:
    """Test the GPIOController class."""
    
    @patch('src.gpio_controller.GPIO')
    def test_init(self, mock_gpio):
        """Test GPIOController initialization."""
        mock_pwm = MagicMock()
        mock_gpio.PWM.return_value = mock_pwm
        
        controller = GPIOController()
        
        # Verify GPIO setup calls
        mock_gpio.setmode.assert_called_once()
        assert mock_gpio.setup.call_count == 3  # Button, servo, LED
        
        # Verify PWM setup
        mock_gpio.PWM.assert_called_once()
        mock_pwm.start.assert_called_once_with(0)
        
        assert controller.servo_pwm == mock_pwm
        assert controller._button_callback is None
    
    def test_set_servo_angle(self, mock_gpio_controller):
        """Test set_servo_angle method."""
        controller, mock_gpio, mock_pwm = mock_gpio_controller
        
        with patch('time.sleep') as mock_sleep:
            controller.set_servo_angle(90)
            
            # Verify duty cycle calculation and PWM calls
            expected_duty = 2 + (90 / 18)  # Should be 7.0
            mock_pwm.ChangeDutyCycle.assert_has_calls([
                call(expected_duty),
                call(0)  # Stop signal
            ])
            mock_sleep.assert_called_once_with(0.5)
    
    def test_set_servo_angle_boundary_values(self, mock_gpio_controller):
        """Test set_servo_angle with boundary values."""
        controller, mock_gpio, mock_pwm = mock_gpio_controller
        
        with patch('time.sleep'):
            # Test minimum angle (0 degrees)
            controller.set_servo_angle(0)
            expected_duty_min = 2 + (0 / 18)  # Should be 2.0
            
            # Test maximum angle (180 degrees)
            controller.set_servo_angle(180)
            expected_duty_max = 2 + (180 / 18)  # Should be 12.0
            
            # Verify calls include both boundary values
            calls = mock_pwm.ChangeDutyCycle.call_args_list
            duty_values = [call[0][0] for call in calls if call[0][0] != 0]
            assert expected_duty_min in duty_values
            assert expected_duty_max in duty_values
    
    def test_rotate_servo(self, mock_gpio_controller):
        """Test rotate_servo method."""
        controller, mock_gpio, mock_pwm = mock_gpio_controller
        
        with patch('time.sleep') as mock_sleep:
            with patch('builtins.print') as mock_print:
                controller.rotate_servo()
                
                # Should call ChangeDutyCycle for each angle from 0 to 159
                assert mock_pwm.ChangeDutyCycle.call_count == 160
                
                # Should sleep between each angle change
                assert mock_sleep.call_count == 160
                
                # Verify print statements
                assert mock_print.call_count == 160
    
    def test_set_led_on(self, mock_gpio_controller):
        """Test set_led method with True (ON)."""
        controller, mock_gpio, mock_pwm = mock_gpio_controller
        
        controller.set_led(True)
        
        # Should output HIGH to LED pin
        mock_gpio.output.assert_called_once()
        call_args = mock_gpio.output.call_args[0]
        assert call_args[1] == mock_gpio.HIGH
    
    def test_set_led_off(self, mock_gpio_controller):
        """Test set_led method with False (OFF)."""
        controller, mock_gpio, mock_pwm = mock_gpio_controller
        
        controller.set_led(False)
        
        # Should output LOW to LED pin
        mock_gpio.output.assert_called_once()
        call_args = mock_gpio.output.call_args[0]
        assert call_args[1] == mock_gpio.LOW
    
    def test_register_button_callback(self, mock_gpio_controller):
        """Test register_button_callback method."""
        controller, mock_gpio, mock_pwm = mock_gpio_controller
        
        mock_callback = Mock()
        controller.register_button_callback(mock_callback)
        
        assert controller._button_callback == mock_callback
        mock_gpio.add_event_detect.assert_called_once()
        
        # Verify event detection parameters
        call_args = mock_gpio.add_event_detect.call_args
        assert call_args[1]['callback'] == mock_callback
        assert call_args[1]['bouncetime'] == 300
    
    @patch('threading.Thread')
    def test_start_monitoring(self, mock_thread, mock_gpio_controller):
        """Test start_monitoring method."""
        controller, mock_gpio, mock_pwm = mock_gpio_controller
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        result = controller.start_monitoring()
        
        # Verify thread creation and start
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        assert result == mock_thread_instance
        
        # Verify daemon flag is set
        thread_kwargs = mock_thread.call_args[1]
        assert thread_kwargs['daemon'] is True
    
    def test_cleanup(self, mock_gpio_controller):
        """Test cleanup method."""
        controller, mock_gpio, mock_pwm = mock_gpio_controller
        
        controller.cleanup()
        
        mock_pwm.stop.assert_called_once()
        mock_gpio.cleanup.assert_called_once()


class TestGPIOControllerIntegration:
    """Integration tests for GPIOController with mocked hardware."""
    
    @pytest.mark.integration
    @patch('src.gpio_controller.GPIO')
    def test_full_servo_sequence(self, mock_gpio):
        """Test a complete servo operation sequence."""
        mock_pwm = MagicMock()
        mock_gpio.PWM.return_value = mock_pwm
        
        controller = GPIOController()
        
        with patch('time.sleep'):
            # Set various angles
            angles = [0, 45, 90, 135, 180]
            for angle in angles:
                controller.set_servo_angle(angle)
            
            # Verify all angles were set
            duty_calls = [call for call in mock_pwm.ChangeDutyCycle.call_args_list 
                         if call[0][0] != 0]  # Exclude stop signals
            
            assert len(duty_calls) == len(angles)
    
    @pytest.mark.integration
    @patch('src.gpio_controller.GPIO')
    def test_led_sequence(self, mock_gpio):
        """Test LED on/off sequence."""
        mock_pwm = MagicMock()
        mock_gpio.PWM.return_value = mock_pwm
        
        controller = GPIOController()
        
        # Test LED sequence: OFF -> ON -> OFF -> ON
        sequence = [False, True, False, True]
        for state in sequence:
            controller.set_led(state)
        
        # Verify correct number of calls
        assert mock_gpio.output.call_count == len(sequence)
        
        # Verify correct states
        output_calls = mock_gpio.output.call_args_list
        expected_states = [mock_gpio.LOW, mock_gpio.HIGH, mock_gpio.LOW, mock_gpio.HIGH]
        
        for i, (call, expected_state) in enumerate(zip(output_calls, expected_states)):
            assert call[0][1] == expected_state, f"LED state {i} incorrect"
