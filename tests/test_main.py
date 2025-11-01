"""
Unit tests for the main module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from src import main


class TestMain:
    """Test the main module and application entry point."""
    
    @patch('src.main.trickster_controller')
    @patch('src.main.app')
    @patch('src.main.print_api_info')
    def test_main_success(self, mock_print_api, mock_app, mock_controller):
        """Test successful main function execution."""
        mock_thread = Mock()
        mock_controller.start_monitoring.return_value = mock_thread
        
        with patch('builtins.print') as mock_print:
            main.main()
            
            # Verify initialization sequence
            mock_controller.initialize.assert_called_once()
            mock_controller.start_monitoring.assert_called_once()
            mock_print_api.assert_called_once()
            
            # Verify Flask app starts
            mock_app.run.assert_called_once()
            
            # Verify startup messages
            expected_prints = [
                call("🎃 Trickster Pi Halloween System Starting... 👻"),
                call("Starting REST API server..."),
                call("Press Ctrl+C to exit.")
            ]
            mock_print.assert_has_calls(expected_prints)
    
    @patch('src.main.trickster_controller')
    @patch('src.main.app')
    @patch('src.main.print_api_info')
    def test_main_keyboard_interrupt(self, mock_print_api, mock_app, mock_controller):
        """Test main function with keyboard interrupt."""
        mock_app.run.side_effect = KeyboardInterrupt()
        
        with patch('builtins.print') as mock_print:
            main.main()
            
            # Verify cleanup is called even with interrupt
            mock_controller.cleanup.assert_called_once()
            
            # Verify exit messages
            exit_prints = [call for call in mock_print.call_args_list 
                          if "Exiting" in str(call) or "Happy Halloween" in str(call)]
            assert len(exit_prints) >= 1
    
    @patch('src.main.trickster_controller')
    @patch('src.main.app')
    @patch('src.main.print_api_info')
    def test_main_exception_handling(self, mock_print_api, mock_app, mock_controller):
        """Test main function with unexpected exception."""
        mock_controller.initialize.side_effect = Exception("Initialization failed")
        
        with patch('builtins.print') as mock_print:
            # Should not raise exception
            main.main()
            
            # Cleanup should still be called
            mock_controller.cleanup.assert_called_once()
    
    @patch('src.main.trickster_controller')
    @patch('src.main.app')
    @patch('src.main.print_api_info')
    def test_main_flask_configuration(self, mock_print_api, mock_app, mock_controller):
        """Test Flask app configuration in main function."""
        main.main()
        
        # Verify Flask app.run called with correct parameters
        mock_app.run.assert_called_once()
        call_kwargs = mock_app.run.call_args[1]
        
        # Should use configuration from config module
        from src.config import API_HOST, API_PORT, API_DEBUG
        assert call_kwargs['host'] == API_HOST
        assert call_kwargs['port'] == API_PORT
        assert call_kwargs['debug'] == API_DEBUG
    
    def test_main_as_script(self):
        """Test main function when called as script."""
        with patch('src.main.main') as mock_main_func:
            with patch('__main__.__name__', '__main__'):
                # Simulate running the module as a script
                exec(compile(open('src/main.py').read(), 'src/main.py', 'exec'))
                
                # Note: This test is more complex due to module execution
                # In a real scenario, you might use subprocess to test script execution


class TestMainIntegration:
    """Integration tests for the main module."""
    
    @pytest.mark.integration
    @patch('src.main.app')
    def test_full_startup_sequence(self, mock_app):
        """Test complete startup sequence integration."""
        with patch('src.main.trickster_controller') as mock_controller:
            with patch('src.main.print_api_info') as mock_print_api:
                with patch('builtins.print') as mock_print:
                    
                    # Mock successful startup
                    mock_thread = Mock()
                    mock_controller.start_monitoring.return_value = mock_thread
                    
                    main.main()
                    
                    # Verify complete startup sequence
                    assert mock_controller.initialize.called
                    assert mock_controller.start_monitoring.called
                    assert mock_print_api.called
                    assert mock_app.run.called
                    assert mock_controller.cleanup.called
                    
                    # Verify all startup messages printed
                    print_messages = [call[0][0] for call in mock_print.call_args_list]
                    startup_message = "🎃 Trickster Pi Halloween System Starting... 👻"
                    assert startup_message in print_messages
    
    @pytest.mark.integration
    @patch('time.sleep')
    @patch('src.main.app')
    def test_graceful_shutdown(self, mock_app, mock_sleep):
        """Test graceful shutdown handling."""
        with patch('src.main.trickster_controller') as mock_controller:
            # Simulate KeyboardInterrupt during app.run
            mock_app.run.side_effect = KeyboardInterrupt("User interrupt")
            
            with patch('builtins.print') as mock_print:
                main.main()
                
                # Verify cleanup was called despite interrupt
                mock_controller.cleanup.assert_called_once()
                
                # Verify shutdown message
                print_messages = [str(call) for call in mock_print.call_args_list]
                shutdown_messages = [msg for msg in print_messages 
                                   if "Exiting" in msg or "Halloween" in msg]
                assert len(shutdown_messages) >= 1


class TestMainErrorScenarios:
    """Test error scenarios in the main module."""
    
    @patch('src.main.app')
    @patch('src.main.trickster_controller')
    def test_controller_init_failure(self, mock_controller, mock_app):
        """Test handling of controller initialization failure."""
        mock_controller.initialize.side_effect = Exception("Hardware not found")
        
        with patch('builtins.print'):
            # Should handle exception gracefully
            main.main()
            
            # Cleanup should still be attempted
            mock_controller.cleanup.assert_called_once()
    
    @patch('src.main.app')
    @patch('src.main.trickster_controller')  
    def test_gpio_monitoring_failure(self, mock_controller, mock_app):
        """Test handling of GPIO monitoring start failure."""
        mock_controller.start_monitoring.side_effect = Exception("GPIO error")
        
        with patch('builtins.print'):
            main.main()
            
            # Should still attempt to start Flask app
            mock_app.run.assert_called_once()
    
    @patch('src.main.trickster_controller')
    def test_flask_startup_failure(self, mock_controller):
        """Test handling of Flask app startup failure."""
        with patch('src.main.app') as mock_app:
            mock_app.run.side_effect = Exception("Port already in use")
            
            with patch('builtins.print'):
                main.main()
                
                # Should still call cleanup
                mock_controller.cleanup.assert_called_once()
    
    @patch('src.main.app')
    @patch('src.main.trickster_controller')
    def test_cleanup_failure(self, mock_controller, mock_app):
        """Test handling of cleanup failure."""
        mock_app.run.side_effect = KeyboardInterrupt()
        mock_controller.cleanup.side_effect = Exception("Cleanup failed")
        
        with patch('builtins.print'):
            # Should not raise exception even if cleanup fails
            main.main()
            
            # Cleanup should have been attempted
            mock_controller.cleanup.assert_called_once()
