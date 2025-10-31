import pygame
import time
import os
import random
from threading import Thread

import RPi.GPIO as GPIO

# GPIO pin definitions
BUTTON_PIN = 17
SERVO_PIN = 12
LED_PIN = 16  # Optional status LED

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)

# Setup PWM for servo (50Hz frequency)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)

# Initialize pygame mixer for audio
pygame.mixer.init()

# Audio folder path
AUDIO_FOLDER = "/mnt/samba/"  # Replace with your audio folder path

# List to store preloaded pygame Sound objects
preloaded_sounds = []

def load_audio_files():
    """Load and preload all .wav and .mp3 files from the specified folder"""
    global preloaded_sounds
    preloaded_sounds = []
    
    if not os.path.exists(AUDIO_FOLDER):
        print(f"Warning: Audio folder '{AUDIO_FOLDER}' does not exist.")
        return
    
    try:
        for filename in os.listdir(AUDIO_FOLDER):
            if filename.lower().endswith(('.wav', '.mp3')):
                full_path = os.path.join(AUDIO_FOLDER, filename)
                
                try:
                    # Preload the audio file into pygame mixer
                    sound = pygame.mixer.Sound(full_path)
                    preloaded_sounds.append(sound)
                    print(f"  Preloaded: {filename}")
                    
                except pygame.error as e:
                    print(f"  Failed to load {filename}: {e}")
                    continue
        
        print(f"Successfully preloaded {len(preloaded_sounds)} audio files from {AUDIO_FOLDER}")
        if not preloaded_sounds:
            print("No valid .wav or .mp3 files found or loaded in the audio folder.")
            
    except Exception as e:
        print(f"Error loading audio files: {e}")

def set_servo_angle(angle):
    """Set servo to specific angle (0-180 degrees)"""
    duty_cycle = 2 + (angle / 18)
    servo_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)
    servo_pwm.ChangeDutyCycle(0)  # Stop sending signal

def play_audio():
    """Play a random preloaded audio file"""
    if not preloaded_sounds:
        print("No audio files available to play.")
        return
    
    try:
        # Select a random preloaded sound and corresponding filename
        sound_index = random.randint(0, len(preloaded_sounds) - 1)
        selected_sound = preloaded_sounds[sound_index]
        
        # Play the preloaded sound
        selected_sound.play()
        
        # Wait for the sound to finish playing
        while pygame.mixer.get_busy():
            time.sleep(0.1)
            
    except Exception as e:
        print(f"Error playing audio: {e}")

def rotate_servo():
    """Rotate servo from 0 to 180 degrees and back"""
    angles = [0, 90, 180, 90, 0]
    for angle in angles:
        set_servo_angle(angle)
        time.sleep(0.5)

def button_callback(channel):
    """Handle button press"""
    print("Button pressed!")
    GPIO.output(LED_PIN, GPIO.HIGH)
    
    # Start audio and servo in parallel threads
    audio_thread = Thread(target=play_audio)
    servo_thread = Thread(target=rotate_servo)
    
    audio_thread.start()
    servo_thread.start()
    
    # Wait for both to complete
    audio_thread.join()
    servo_thread.join()
    
    GPIO.output(LED_PIN, GPIO.LOW)
    print("Action completed!")

def main():
    # Load audio files at startup
    load_audio_files()
    
    # Test the button callback
    button_callback(1)

    try:
        # Add button press detection
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, 
                            callback=button_callback, bouncetime=300)
        
        print("System ready. Press button to activate.")
        print("Press Ctrl+C to exit.")
        
        # Keep program running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Cleanup
        servo_pwm.stop()
        GPIO.cleanup()
        pygame.mixer.quit()

if __name__ == "__main__":
    main()
