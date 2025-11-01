"""
GPIO controller module for the Trickster Pi Halloween project.
Handles servo motor, LED, and button GPIO operations.
"""

import time
import random
from threading import Thread
from typing import Callable, Optional

import RPi.GPIO as GPIO

from config import BUTTON_PIN, SERVO_PIN, LED_PIN, SERVO_PWM_FREQUENCY


class GPIOController:
    """Manages GPIO operations for servo, LED, and button."""
    
    def __init__(self):
        """Initialize GPIO controller."""
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        GPIO.setup(LED_PIN, GPIO.OUT)
        
        # Setup PWM for servo
        self.servo_pwm = GPIO.PWM(SERVO_PIN, SERVO_PWM_FREQUENCY)
        self.servo_pwm.start(0)
        
        # Button callback reference
        self._button_callback: Optional[Callable] = None
    
    def set_servo_angle(self, angle: float) -> None:
        """Set servo to specific angle (0-180 degrees)."""
        duty_cycle = 2 + (angle / 18)
        self.servo_pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)
        self.servo_pwm.ChangeDutyCycle(0)  # Stop sending signal
    
    def rotate_servo(self) -> None:
        """Rotate servo from 0 to 160 degrees smoothly."""
        for angle in range(0, 160, 1):
            duty = float(angle) / 18 + 2
            print(duty, angle)
            self.servo_pwm.ChangeDutyCycle(duty)
            time.sleep(0.01)
    
    def set_led(self, state: bool) -> None:
        """Set LED state (True = ON, False = OFF)."""
        GPIO.output(LED_PIN, GPIO.HIGH if state else GPIO.LOW)
    
    def register_button_callback(self, callback: Callable) -> None:
        """Register a callback function for button press events."""
        self._button_callback = callback
        
        # Add button press detection
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, 
                            callback=self._button_callback, bouncetime=300)
    
    def start_monitoring(self) -> None:
        """Start GPIO monitoring in a separate thread."""
        def monitor_loop():
            try:
                print("GPIO monitoring started. Press button to activate.")
                
                # Keep GPIO monitoring running
                while True:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"GPIO monitoring error: {e}")
        
        gpio_thread = Thread(target=monitor_loop, daemon=True)
        gpio_thread.start()
        return gpio_thread
    
    def cleanup(self) -> None:
        """Clean up GPIO resources."""
        self.servo_pwm.stop()
        GPIO.cleanup()


# Global GPIO controller instance
gpio_controller = GPIOController()
