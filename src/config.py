"""
Configuration constants for the Trickster Pi Halloween project.
"""

# GPIO pin definitions
BUTTON_PIN = 17
SERVO_PIN = 12
LED_PIN = 16  # Optional status LED

# Audio configuration
AUDIO_FOLDER = "/mnt/samba/"  # Replace with your audio folder path
TARGET_AUDIO_DURATION = 60  # Minimum audio sequence duration in seconds

# Timing configuration
MIN_DELAY = 10  # Minimum delay before servo activation (seconds)
MAX_DELAY = 20  # Maximum delay before servo activation (seconds)
MIN_PAUSE_BETWEEN_SOUNDS = 0.5  # Minimum pause between audio files (seconds)
MAX_PAUSE_BETWEEN_SOUNDS = 2.0  # Maximum pause between audio files (seconds)

# API configuration
API_HOST = '0.0.0.0'
API_PORT = 5000
API_DEBUG = False

# Servo configuration
SERVO_PWM_FREQUENCY = 50  # PWM frequency for servo (Hz)
