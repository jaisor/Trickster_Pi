import pygame
import time
import os
import random
from threading import Thread

import RPi.GPIO as GPIO
from flask import Flask, jsonify

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

# Initialize Flask app
app = Flask(__name__)

# Audio folder path
AUDIO_FOLDER = "/mnt/samba/"  # Replace with your audio folder path

# List to store preloaded pygame Sound objects
preloaded_sounds = []
# List to store audio filenames for API responses
audio_filenames = []

# Flag to track if callback is in progress
callback_in_progress = False

def load_audio_files():
    """Load and preload all .wav and .mp3 files from the specified folder"""
    global preloaded_sounds, audio_filenames
    preloaded_sounds = []
    audio_filenames = []
    
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
                    audio_filenames.append(filename)
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
#    time.sleep(0.5)
#    servo_pwm.ChangeDutyCycle(0)  # Stop sending signal

def play_audio():
    """Play multiple random audio files in sequence for at least 60 seconds"""
    if not preloaded_sounds:
        print("No audio files available to play.")
        return
    
    try:
        start_time = time.time()
        target_duration = 60  # At least 60 seconds of audio
        sounds_played = []
        
        print("Starting extended audio sequence...")
        
        while (time.time() - start_time) < target_duration:
            # Select a random preloaded sound and corresponding filename
            sound_index = random.randint(0, len(preloaded_sounds) - 1)
            selected_sound = preloaded_sounds[sound_index]
            selected_filename = audio_filenames[sound_index]
            
            print(f"  Playing: {selected_filename}")
            sounds_played.append(selected_filename)
            
            # Play the preloaded sound
            selected_sound.play()
            
            # Wait for the sound to finish playing
            while pygame.mixer.get_busy():
                time.sleep(0.1)
            
            # Add a small pause between sounds (0.5-2 seconds)
            pause = random.uniform(0.5, 2.0)
            time.sleep(pause)
        
        elapsed_time = time.time() - start_time
        print(f"Audio sequence completed: {len(sounds_played)} sounds played over {elapsed_time:.1f} seconds")
            
    except Exception as e:
        print(f"Error playing audio: {e}")

def play_random_sound():
    """Play a random sound and return information about it"""
    if not preloaded_sounds:
        return {"success": False, "message": "No audio files available to play."}
    
    try:
        # Select a random preloaded sound and corresponding filename
        sound_index = random.randint(0, len(preloaded_sounds) - 1)
        selected_sound = preloaded_sounds[sound_index]
        selected_filename = audio_filenames[sound_index]
        
        print(f"Playing: {selected_filename}")
        
        # Play the preloaded sound (non-blocking)
        selected_sound.play()
        
        return {
            "success": True, 
            "message": f"Playing {selected_filename}",
            "filename": selected_filename,
            "total_sounds": len(preloaded_sounds)
        }
            
    except Exception as e:
        error_msg = f"Error playing audio: {e}"
        print(error_msg)
        return {"success": False, "message": error_msg}

def rotate_servo():
    """Rotate servo"""
    set_servo_angle(160)
    time.sleep(3)
    set_servo_angle(10)

def button_callback(channel):
    """Handle button press with random delay and ignore concurrent presses"""
    global callback_in_progress
    
    # Ignore button press if callback is already in progress
    if callback_in_progress:
        print("Button press ignored - action already in progress")
        return
    
    print("Button pressed!")
    callback_in_progress = True
    
    try:
        # Turn on LED to indicate button press received
        GPIO.output(LED_PIN, GPIO.HIGH)
        
        # Start audio thread immediately (before delay)
        print("Starting extended audio sequence...")
        audio_thread = Thread(target=play_audio)
        audio_thread.start()
        
        # Random delay between 10-20 seconds for servo activation
        delay = random.uniform(10, 20)
        print(f"Waiting {delay:.1f} seconds before servo activation...")
        time.sleep(delay)
        
        print("Activating servo now!")
        
        # Start servo thread
        servo_thread = Thread(target=rotate_servo)
        servo_thread.start()
        
        # Wait for both to complete
        audio_thread.join()
        servo_thread.join()
        
        print("Action completed!")
        
    finally:
        # Always reset the flag and turn off LED
        GPIO.output(LED_PIN, GPIO.LOW)
        callback_in_progress = False

# REST API Endpoints
@app.route('/play', methods=['GET'])
def api_play_sound():
    """REST API endpoint to play a random sound"""
    result = play_random_sound()
    return jsonify(result)

@app.route('/serv', methods=['GET'])
def api_serv():
    """REST API endpoint to serv"""
    result = rotate_servo()
    return jsonify(result)

@app.route('/status', methods=['GET'])
def api_status():
    """REST API endpoint to get system status"""
    return jsonify({
        "status": "running",
        "total_sounds": len(preloaded_sounds),
        "sounds_loaded": len(preloaded_sounds) > 0,
        "audio_folder": AUDIO_FOLDER
    })

@app.route('/sounds', methods=['GET'])
def api_list_sounds():
    """REST API endpoint to list all available sounds"""
    return jsonify({
        "total_sounds": len(preloaded_sounds),
        "sounds": audio_filenames
    })

@app.route('/trigger', methods=['GET'])
def api_trigger_delayed():
    """REST API endpoint to trigger delayed action like button press"""
    global callback_in_progress
    
    if callback_in_progress:
        return jsonify({
            "success": False,
            "message": "Action already in progress, ignoring trigger"
        })
    
    # Start the delayed callback in a separate thread so API doesn't block
    def delayed_callback():
        button_callback(None)
    
    callback_thread = Thread(target=delayed_callback, daemon=True)
    callback_thread.start()
    
    return jsonify({
        "success": True,
        "message": "Delayed action triggered (10-20 second random delay)",
        "delay_range": "10-20 seconds"
    })

@app.route('/reload', methods=['GET'])
def api_reload_sounds():
    """REST API endpoint to reload all audio files from the folder"""
    try:
        # Store the previous count for comparison
        previous_count = len(preloaded_sounds)
        
        # Reload the audio files
        load_audio_files()
        
        # Get the new count
        new_count = len(preloaded_sounds)
        
        return jsonify({
            "success": True,
            "message": f"Audio files reloaded successfully",
            "previous_count": previous_count,
            "new_count": new_count,
            "change": new_count - previous_count,
            "audio_folder": AUDIO_FOLDER,
            "loaded_files": audio_filenames
        })
        
    except Exception as e:
        error_msg = f"Error reloading audio files: {e}"
        print(error_msg)
        return jsonify({
            "success": False,
            "message": error_msg
        })

def run_gpio_monitor():
    """Run GPIO monitoring in a separate thread"""
    try:
        # Add button press detection
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, 
                            callback=button_callback, bouncetime=300)
        
        print("GPIO monitoring started. Press button to activate.")
        
        # Keep GPIO monitoring running
        while True:
            time.sleep(1)
            
    except Exception as e:
        print(f"GPIO monitoring error: {e}")

def main():

    set_servo_angle(10)

    # Load audio files at startup
    load_audio_files()
    
    # Test the button callback (skip for normal operation - comment out if not testing)
    # button_callback(1)

    try:
        # Start GPIO monitoring in a separate thread
        gpio_thread = Thread(target=run_gpio_monitor, daemon=True)
        gpio_thread.start()
        
        print("Starting REST API server...")
        print("API endpoints available:")
        print("  GET /play - Play a random sound (immediate)")
        print("  GET /trigger - Trigger delayed action (10-20 sec delay)")
        print("  GET /status - Get system status") 
        print("  GET /sounds - List all available sounds")
        print("  GET /reload - Reload audio files from folder")
        print("Press Ctrl+C to exit.")
        
        # Start Flask API server
        app.run(host='0.0.0.0', port=5000, debug=False)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Cleanup
        servo_pwm.stop()
        GPIO.cleanup()
        pygame.mixer.quit()

if __name__ == "__main__":
    main()
