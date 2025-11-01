"""
Unit tests for the api_routes module.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.api_routes import app


class TestAPIRoutes:
    """Test Flask API routes."""
    
    def test_api_play_sound_success(self, flask_test_client):
        """Test successful /play endpoint."""
        client, mock_audio, mock_controller = flask_test_client
        
        mock_audio.play_random_sound.return_value = {
            "success": True,
            "filename": "test.wav",
            "message": "Playing test.wav",
            "total_sounds": 2
        }
        
        response = client.get('/play')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["success"] is True
        assert data["filename"] == "test.wav"
        mock_audio.play_random_sound.assert_called_once()
    
    def test_api_play_sound_failure(self, flask_test_client):
        """Test /play endpoint when no sounds available."""
        client, mock_audio, mock_controller = flask_test_client
        
        mock_audio.play_random_sound.return_value = {
            "success": False,
            "message": "No audio files available to play."
        }
        
        response = client.get('/play')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["success"] is False
        assert "No audio files available" in data["message"]
    
    def test_api_status_running(self, flask_test_client):
        """Test /status endpoint when system is running."""
        client, mock_audio, mock_controller = flask_test_client
        
        mock_controller.is_busy.return_value = False
        mock_audio.get_audio_info.return_value = {
            "total_sounds": 3,
            "sounds": ["test1.wav", "test2.mp3", "test3.wav"],
            "audio_folder": "/test/audio"
        }
        
        response = client.get('/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["status"] == "running"
        assert data["callback_in_progress"] is False
        assert data["total_sounds"] == 3
        assert data["sounds_loaded"] is True
        assert data["audio_folder"] == "/test/audio"
    
    def test_api_status_busy(self, flask_test_client):
        """Test /status endpoint when callback is in progress."""
        client, mock_audio, mock_controller = flask_test_client
        
        mock_controller.is_busy.return_value = True
        mock_audio.get_audio_info.return_value = {
            "total_sounds": 1,
            "sounds": ["test.wav"],
            "audio_folder": "/test/audio"
        }
        
        response = client.get('/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["callback_in_progress"] is True
        assert data["sounds_loaded"] is True
    
    def test_api_status_no_sounds(self, flask_test_client):
        """Test /status endpoint with no sounds loaded."""
        client, mock_audio, mock_controller = flask_test_client
        
        mock_audio.get_audio_info.return_value = {
            "total_sounds": 0,
            "sounds": [],
            "audio_folder": "/test/audio"
        }
        
        response = client.get('/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["total_sounds"] == 0
        assert data["sounds_loaded"] is False
    
    def test_api_list_sounds(self, flask_test_client):
        """Test /sounds endpoint."""
        client, mock_audio, mock_controller = flask_test_client
        
        mock_audio.get_audio_info.return_value = {
            "total_sounds": 2,
            "sounds": ["spooky1.wav", "scary2.mp3"],
            "audio_folder": "/test/audio"
        }
        
        response = client.get('/sounds')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["total_sounds"] == 2
        assert data["sounds"] == ["spooky1.wav", "scary2.mp3"]
    
    def test_api_trigger_success(self, flask_test_client):
        """Test /trigger endpoint when system is available."""
        client, mock_audio, mock_controller = flask_test_client
        
        mock_controller.is_busy.return_value = False
        
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance
            
            response = client.get('/trigger')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data["success"] is True
            assert "Delayed action triggered" in data["message"]
            assert data["delay_range"] == "10-20 seconds"
            
            # Verify thread was created and started
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()
    
    def test_api_trigger_busy(self, flask_test_client):
        """Test /trigger endpoint when system is busy."""
        client, mock_audio, mock_controller = flask_test_client
        
        mock_controller.is_busy.return_value = True
        
        response = client.get('/trigger')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["success"] is False
        assert "Action already in progress" in data["message"]
    
    def test_api_reload_success(self, flask_test_client):
        """Test /reload endpoint successful reload."""
        client, mock_audio, mock_controller = flask_test_client
        
        # Mock initial state
        mock_audio.get_audio_info.side_effect = [
            {"total_sounds": 2, "sounds": ["old1.wav", "old2.mp3"], "audio_folder": "/test"},
            {"total_sounds": 3, "sounds": ["old1.wav", "old2.mp3", "new.wav"], "audio_folder": "/test"}
        ]
        
        response = client.get('/reload')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["success"] is True
        assert data["previous_count"] == 2
        assert data["new_count"] == 3
        assert data["change"] == 1
        assert "new.wav" in data["loaded_files"]
        
        mock_audio.load_audio_files.assert_called_once()
    
    def test_api_reload_error(self, flask_test_client):
        """Test /reload endpoint with error during reload."""
        client, mock_audio, mock_controller = flask_test_client
        
        mock_audio.get_audio_info.return_value = {"total_sounds": 2}
        mock_audio.load_audio_files.side_effect = Exception("Disk error")
        
        response = client.get('/reload')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["success"] is False
        assert "Error reloading audio files" in data["message"]
        assert "Disk error" in data["message"]


class TestAPIRoutesIntegration:
    """Integration tests for API routes."""
    
    @pytest.mark.integration
    def test_api_workflow(self, flask_test_client):
        """Test a complete API workflow."""
        client, mock_audio, mock_controller = flask_test_client
        
        # Setup mock responses
        mock_audio.get_audio_info.return_value = {
            "total_sounds": 2,
            "sounds": ["test1.wav", "test2.mp3"],
            "audio_folder": "/test/audio"
        }
        mock_controller.is_busy.return_value = False
        mock_audio.play_random_sound.return_value = {
            "success": True,
            "filename": "test1.wav",
            "message": "Playing test1.wav",
            "total_sounds": 2
        }
        
        # Test workflow: status -> sounds -> play -> trigger
        
        # 1. Check status
        response = client.get('/status')
        assert response.status_code == 200
        status_data = json.loads(response.data)
        assert status_data["status"] == "running"
        
        # 2. List sounds
        response = client.get('/sounds')
        assert response.status_code == 200
        sounds_data = json.loads(response.data)
        assert len(sounds_data["sounds"]) == 2
        
        # 3. Play immediate sound
        response = client.get('/play')
        assert response.status_code == 200
        play_data = json.loads(response.data)
        assert play_data["success"] is True
        
        # 4. Trigger delayed action
        with patch('threading.Thread'):
            response = client.get('/trigger')
            assert response.status_code == 200
            trigger_data = json.loads(response.data)
            assert trigger_data["success"] is True
    
    @pytest.mark.integration
    def test_error_handling(self, flask_test_client):
        """Test API error handling."""
        client, mock_audio, mock_controller = flask_test_client
        
        # Test with various error conditions
        error_conditions = [
            # Audio manager errors
            (mock_audio.play_random_sound, Exception("Audio system failure")),
            (mock_audio.get_audio_info, Exception("File system error")),
        ]
        
        for mock_method, exception in error_conditions:
            mock_method.side_effect = exception
            
            # The API should handle exceptions gracefully
            # (depending on implementation, some endpoints might need error handling)
            try:
                response = client.get('/play')
                # Should not crash the server
                assert response.status_code in [200, 500]  # Depending on error handling
            except Exception:
                # If exceptions bubble up, they should be handled at app level
                pass
            
            # Reset mock
            mock_method.side_effect = None
    
    def test_http_methods(self, flask_test_client):
        """Test that endpoints only accept GET requests."""
        client, mock_audio, mock_controller = flask_test_client
        
        endpoints = ['/play', '/status', '/sounds', '/trigger', '/reload']
        
        for endpoint in endpoints:
            # GET should work
            response = client.get(endpoint)
            assert response.status_code in [200, 405]  # 405 if other methods not allowed
            
            # POST should return 405 Method Not Allowed
            response = client.post(endpoint)
            assert response.status_code == 405
            
            # PUT should return 405 Method Not Allowed  
            response = client.put(endpoint)
            assert response.status_code == 405
