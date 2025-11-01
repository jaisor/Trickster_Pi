"""
Audio management module for the Trickster Pi Halloween project.
Handles loading, preloading, and playback of audio files.
"""

import pygame
import os
import random
import time
from typing import List, Dict, Any

from config import AUDIO_FOLDER, TARGET_AUDIO_DURATION, MIN_PAUSE_BETWEEN_SOUNDS, MAX_PAUSE_BETWEEN_SOUNDS


class AudioManager:
    """Manages audio file loading and playback operations."""
    
    def __init__(self):
        """Initialize the audio manager."""
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Storage for preloaded sounds
        self.preloaded_sounds: List[pygame.mixer.Sound] = []
        self.audio_filenames: List[str] = []
    
    def load_audio_files(self) -> None:
        """Load and preload all .wav and .mp3 files from the specified folder."""
        self.preloaded_sounds = []
        self.audio_filenames = []
        
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
                        self.preloaded_sounds.append(sound)
                        self.audio_filenames.append(filename)
                        print(f"  Preloaded: {filename}")
                        
                    except pygame.error as e:
                        print(f"  Failed to load {filename}: {e}")
                        continue
            
            print(f"Successfully preloaded {len(self.preloaded_sounds)} audio files from {AUDIO_FOLDER}")
            if not self.preloaded_sounds:
                print("No valid .wav or .mp3 files found or loaded in the audio folder.")
                
        except Exception as e:
            print(f"Error loading audio files: {e}")
    
    def play_audio_sequence(self) -> None:
        """Play multiple random audio files in sequence for at least the target duration."""
        if not self.preloaded_sounds:
            print("No audio files available to play.")
            return
        
        try:
            start_time = time.time()
            sounds_played = []
            
            print("Starting extended audio sequence...")
            
            while (time.time() - start_time) < TARGET_AUDIO_DURATION:
                # Select a random preloaded sound and corresponding filename
                sound_index = random.randint(0, len(self.preloaded_sounds) - 1)
                selected_sound = self.preloaded_sounds[sound_index]
                selected_filename = self.audio_filenames[sound_index]
                
                print(f"  Playing: {selected_filename}")
                sounds_played.append(selected_filename)
                
                # Play the preloaded sound
                selected_sound.play()
                
                # Wait for the sound to finish playing
                while pygame.mixer.get_busy():
                    time.sleep(0.1)
                
                # Add a small pause between sounds
                pause = random.uniform(MIN_PAUSE_BETWEEN_SOUNDS, MAX_PAUSE_BETWEEN_SOUNDS)
                time.sleep(pause)
            
            elapsed_time = time.time() - start_time
            print(f"Audio sequence completed: {len(sounds_played)} sounds played over {elapsed_time:.1f} seconds")
                
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def play_random_sound(self) -> Dict[str, Any]:
        """Play a random sound and return information about it."""
        if not self.preloaded_sounds:
            return {"success": False, "message": "No audio files available to play."}
        
        try:
            # Select a random preloaded sound and corresponding filename
            sound_index = random.randint(0, len(self.preloaded_sounds) - 1)
            selected_sound = self.preloaded_sounds[sound_index]
            selected_filename = self.audio_filenames[sound_index]
            
            print(f"Playing: {selected_filename}")
            
            # Play the preloaded sound (non-blocking)
            selected_sound.play()
            
            return {
                "success": True, 
                "message": f"Playing {selected_filename}",
                "filename": selected_filename,
                "total_sounds": len(self.preloaded_sounds)
            }
                
        except Exception as e:
            error_msg = f"Error playing audio: {e}"
            print(error_msg)
            return {"success": False, "message": error_msg}
    
    def get_audio_info(self) -> Dict[str, Any]:
        """Get information about loaded audio files."""
        return {
            "total_sounds": len(self.preloaded_sounds),
            "sounds": self.audio_filenames.copy(),
            "audio_folder": AUDIO_FOLDER
        }
    
    def cleanup(self) -> None:
        """Clean up audio resources."""
        pygame.mixer.quit()


# Global audio manager instance
audio_manager = AudioManager()
