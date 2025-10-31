import pygame
import time
from threading import Thread

import RPi.GPIO as GPIO

# GPIO pin definitions
BUTTON_PIN = 18
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

# Audio file path
AUDIO_FILE = "audio.mp3"  # Replace with your MP3 file path

def set_servo_angle(angle):
    """Set servo to specific angle (0-180 degrees)"""
    duty_cycle = 2 + (angle / 18)
    servo_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)
    servo_pwm.ChangeDutyCycle(0)  # Stop sending signal

def play_audio():
    """Play MP3 file"""
    try:
        pygame.mixer.music.load(AUDIO_FILE)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except pygame.error as e:
        print(f"Audio error: {e}")

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
