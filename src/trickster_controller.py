"""
Main trickster controller module for the Trickster Pi Halloween project.
Orchestrates the Halloween scare sequence with audio and servo actions.
"""

import time
import random
from threading import Thread
from typing import Optional

from config import MIN_DELAY, MAX_DELAY
from audio_manager import audio_manager
from gpio_controller import gpio_controller


class TricksterController:
    """Main controller that orchestrates the Halloween scare sequence."""
    
    def __init__(self):
        """Initialize the trickster controller."""
        self.callback_in_progress = False
    
    def button_callback(self, channel: Optional[int]) -> None:
        """Handle button press with random delay and ignore concurrent presses."""
        # Ignore button press if callback is already in progress
        if self.callback_in_progress:
            print("Button press ignored - action already in progress")
            return
        
        print("Button pressed!")
        self.callback_in_progress = True
        
        try:
            # Turn on LED to indicate button press received
            gpio_controller.set_led(True)
            
            # Start audio thread immediately (before delay)
            print("Starting extended audio sequence...")
            audio_thread = Thread(target=audio_manager.play_audio_sequence)
            audio_thread.start()
            
            # Random delay between MIN_DELAY-MAX_DELAY seconds for servo activation
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            print(f"Waiting {delay:.1f} seconds before servo activation...")
            time.sleep(delay)
            
            print("Activating servo now!")
            
            # Start servo thread
            servo_thread = Thread(target=gpio_controller.rotate_servo)
            servo_thread.start()
            
            # Wait for both to complete
            audio_thread.join()
            servo_thread.join()
            
            print("Action completed!")
            
        finally:
            # Always reset the flag and turn off LED
            gpio_controller.set_led(False)
            self.callback_in_progress = False
    
    def is_busy(self) -> bool:
        """Check if a callback is currently in progress."""
        return self.callback_in_progress
    
    def initialize(self) -> None:
        """Initialize the trickster system."""
        # Load audio files
        audio_manager.load_audio_files()
        
        # Register button callback
        gpio_controller.register_button_callback(self.button_callback)
    
    def start_monitoring(self) -> Thread:
        """Start GPIO monitoring."""
        return gpio_controller.start_monitoring()
    
    def cleanup(self) -> None:
        """Clean up all resources."""
        gpio_controller.cleanup()
        audio_manager.cleanup()


# Global trickster controller instance
trickster_controller = TricksterController()
