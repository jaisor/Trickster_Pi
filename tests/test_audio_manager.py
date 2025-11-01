"""
Unit tests for the audio_manager module.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from src.audio_manager import AudioManager


class TestAudioManager:
    """Test the AudioManager class."""
    
    def test_init(self):
        """Test AudioManager initialization."""
        with patch('pygame.mixer.init') as mock_init:
            manager = AudioManager()
            
            mock_init.assert_called_once()
            assert manager.preloaded_sounds == []
            assert manager.audio_filenames == []
    
    @patch('src.audio_manager.AUDIO_FOLDER', '/test/audio')
    @patch('os.path.exists')
    def test_load_audio_files_missing_folder(self, mock_exists, mock_audio_manager):
        """Test load_audio_files with missing folder."""
        mock_exists.return_value = False
        manager, _, _ = mock_audio_manager
        
        with patch('builtins.print') as mock_print:
            manager.load_audio_files()
            
            mock_print.assert_called_with("Warning: Audio folder '/test/audio' does not exist.")
            assert manager.preloaded_sounds == []
            assert manager.audio_filenames == []
    
    @patch('src.audio_manager.AUDIO_FOLDER')
    @patch('os.path.exists')
    @patch('os.listdir')
    def test_load_audio_files_success(self, mock_listdir, mock_exists, mock_folder, mock_audio_manager):
        """Test successful audio file loading."""
        mock_exists.return_value = True
        mock_folder.return_value = '/test/audio'
        mock_listdir.return_value = ['sound1.wav', 'sound2.mp3', 'sound3.WAV', 'ignore.txt']
        
        manager, mock_sound_class, mock_sound = mock_audio_manager
        
        with patch('builtins.print') as mock_print:
            manager.load_audio_files()
            
            # Should create Sound objects for 3 audio files
            assert mock_sound_class.call_count == 3
            assert len(manager.preloaded_sounds) == 3
            assert len(manager.audio_filenames) == 3
            
            expected_filenames = ['sound1.wav', 'sound2.mp3', 'sound3.WAV']
            assert manager.audio_filenames == expected_filenames
    
    @patch('src.audio_manager.AUDIO_FOLDER')
    @patch('os.path.exists')
    @patch('os.listdir')
    def test_load_audio_files_with_errors(self, mock_listdir, mock_exists, mock_folder, mock_audio_manager):
        """Test audio file loading with some files failing."""
        mock_exists.return_value = True
        mock_folder.return_value = '/test/audio'
        mock_listdir.return_value = ['good.wav', 'bad.mp3']
        
        manager, mock_sound_class, mock_sound = mock_audio_manager
        
        # Make the second file fail to load
        mock_sound_class.side_effect = [Mock(), Exception("File corrupted")]
        
        with patch('builtins.print') as mock_print:
            manager.load_audio_files()
            
            # Should only have one successful load
            assert len(manager.preloaded_sounds) == 1
            assert len(manager.audio_filenames) == 1
            assert manager.audio_filenames == ['good.wav']
    
    def test_play_audio_sequence_no_sounds(self, mock_audio_manager):
        """Test play_audio_sequence with no loaded sounds."""
        manager, _, _ = mock_audio_manager
        manager.preloaded_sounds = []
        
        with patch('builtins.print') as mock_print:
            manager.play_audio_sequence()
            
            mock_print.assert_called_with("No audio files available to play.")
    
    @patch('src.audio_manager.TARGET_AUDIO_DURATION', 2)  # Short duration for testing
    @patch('pygame.mixer.get_busy')
    @patch('time.sleep')
    @patch('time.time')
    @patch('random.randint')
    @patch('random.uniform')
    def test_play_audio_sequence_success(self, mock_uniform, mock_randint, mock_time, 
                                       mock_sleep, mock_get_busy, mock_audio_manager):
        """Test successful audio sequence playback."""
        manager, _, _ = mock_audio_manager
        
        # Set up mock sounds
        mock_sound1 = Mock()
        mock_sound2 = Mock()
        manager.preloaded_sounds = [mock_sound1, mock_sound2]
        manager.audio_filenames = ['sound1.wav', 'sound2.wav']
        
        # Mock time progression
        mock_time.side_effect = [0, 1, 3]  # Start, middle, end (exceeds duration)
        mock_randint.return_value = 0  # Always select first sound
        mock_uniform.return_value = 1.0  # 1 second pause
        mock_get_busy.side_effect = [True, False]  # Sound plays then stops
        
        with patch('builtins.print') as mock_print:
            manager.play_audio_sequence()
            
            # Should play at least one sound
            mock_sound1.play.assert_called()
            mock_sleep.assert_called()
    
    def test_play_random_sound_no_sounds(self, mock_audio_manager):
        """Test play_random_sound with no loaded sounds."""
        manager, _, _ = mock_audio_manager
        manager.preloaded_sounds = []
        
        result = manager.play_random_sound()
        
        assert result["success"] is False
        assert "No audio files available" in result["message"]
    
    @patch('random.randint')
    def test_play_random_sound_success(self, mock_randint, mock_audio_manager):
        """Test successful random sound playback."""
        manager, _, _ = mock_audio_manager
        
        # Set up mock sounds
        mock_sound = Mock()
        manager.preloaded_sounds = [mock_sound]
        manager.audio_filenames = ['test.wav']
        mock_randint.return_value = 0
        
        result = manager.play_random_sound()
        
        assert result["success"] is True
        assert result["filename"] == "test.wav"
        assert result["total_sounds"] == 1
        mock_sound.play.assert_called_once()
    
    def test_get_audio_info(self, mock_audio_manager):
        """Test get_audio_info method."""
        manager, _, _ = mock_audio_manager
        manager.preloaded_sounds = [Mock(), Mock()]
        manager.audio_filenames = ['sound1.wav', 'sound2.mp3']
        
        with patch('src.audio_manager.AUDIO_FOLDER', '/test/folder'):
            info = manager.get_audio_info()
            
            assert info["total_sounds"] == 2
            assert info["sounds"] == ['sound1.wav', 'sound2.mp3']
            assert info["audio_folder"] == '/test/folder'
    
    def test_cleanup(self, mock_audio_manager):
        """Test cleanup method."""
        manager, _, _ = mock_audio_manager
        
        with patch('pygame.mixer.quit') as mock_quit:
            manager.cleanup()
            mock_quit.assert_called_once()
