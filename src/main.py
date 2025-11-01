"""
Main application entry point for the Trickster Pi Halloween project.
"""

from config import API_HOST, API_PORT, API_DEBUG
from trickster_controller import trickster_controller
from api_routes import app, print_api_info


def main():
    """Main application entry point."""
    print("🎃 Trickster Pi Halloween System Starting... 👻")
    
    try:
        # Initialize the trickster system
        trickster_controller.initialize()
        
        # Start GPIO monitoring in a separate thread
        gpio_thread = trickster_controller.start_monitoring()
        
        # Print API information
        print("Starting REST API server...")
        print_api_info()
        print("Press Ctrl+C to exit.")
        
        # Start Flask API server (this blocks)
        app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)
            
    except KeyboardInterrupt:
        print("\n🎃 Exiting Trickster Pi... 👻")
    finally:
        # Cleanup all resources
        trickster_controller.cleanup()
        print("Cleanup completed. Happy Halloween! 🎃")


if __name__ == "__main__":
    main()
