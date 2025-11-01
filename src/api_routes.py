"""
REST API routes module for the Trickster Pi Halloween project.
Defines Flask API endpoints for remote control and monitoring.
"""

from threading import Thread
from flask import Flask, jsonify

from audio_manager import audio_manager
from trickster_controller import trickster_controller

# Initialize Flask app
app = Flask(__name__)


@app.route('/play', methods=['GET'])
def api_play_sound():
    """REST API endpoint to play a random sound (immediate playback)."""
    result = audio_manager.play_random_sound()
    return jsonify(result)


@app.route('/status', methods=['GET'])
def api_status():
    """REST API endpoint to get system status."""
    audio_info = audio_manager.get_audio_info()
    
    return jsonify({
        "status": "running",
        "callback_in_progress": trickster_controller.is_busy(),
        "total_sounds": audio_info["total_sounds"],
        "sounds_loaded": audio_info["total_sounds"] > 0,
        "audio_folder": audio_info["audio_folder"]
    })


@app.route('/sounds', methods=['GET'])
def api_list_sounds():
    """REST API endpoint to list all available sounds."""
    audio_info = audio_manager.get_audio_info()
    
    return jsonify({
        "total_sounds": audio_info["total_sounds"],
        "sounds": audio_info["sounds"]
    })


@app.route('/trigger', methods=['GET'])
def api_trigger_delayed():
    """REST API endpoint to trigger delayed action like button press."""
    if trickster_controller.is_busy():
        return jsonify({
            "success": False,
            "message": "Action already in progress, ignoring trigger"
        })
    
    # Start the delayed callback in a separate thread so API doesn't block
    def delayed_callback():
        trickster_controller.button_callback(None)
    
    callback_thread = Thread(target=delayed_callback, daemon=True)
    callback_thread.start()
    
    return jsonify({
        "success": True,
        "message": "Delayed action triggered (10-20 second random delay)",
        "delay_range": "10-20 seconds"
    })


@app.route('/reload', methods=['GET'])
def api_reload_sounds():
    """REST API endpoint to reload all audio files from the folder."""
    try:
        # Store the previous count for comparison
        previous_info = audio_manager.get_audio_info()
        previous_count = previous_info["total_sounds"]
        
        # Reload the audio files
        audio_manager.load_audio_files()
        
        # Get the new count
        new_info = audio_manager.get_audio_info()
        new_count = new_info["total_sounds"]
        
        return jsonify({
            "success": True,
            "message": "Audio files reloaded successfully",
            "previous_count": previous_count,
            "new_count": new_count,
            "change": new_count - previous_count,
            "audio_folder": new_info["audio_folder"],
            "loaded_files": new_info["sounds"]
        })
        
    except Exception as e:
        error_msg = f"Error reloading audio files: {e}"
        print(error_msg)
        return jsonify({
            "success": False,
            "message": error_msg
        })


def print_api_info():
    """Print information about available API endpoints."""
    print("API endpoints available:")
    print("  GET /play - Play a random sound (immediate)")
    print("  GET /trigger - Trigger delayed action (10-20 sec delay)")
    print("  GET /status - Get system status") 
    print("  GET /sounds - List all available sounds")
    print("  GET /reload - Reload audio files from folder")
