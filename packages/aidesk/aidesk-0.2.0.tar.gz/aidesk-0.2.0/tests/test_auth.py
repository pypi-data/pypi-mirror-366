import unittest
import json
import os
from aidesk.api_handlers.auth import handle_login_api
from unittest.mock import Mock, patch

class TestAuthHandlers(unittest.TestCase):
    
    def setUp(self):
        # Create mock handler
        self.handler = Mock()
        self.handler.send_json_response = Mock()
        
        # Mock headers and other properties
        self.handler.headers = {}
        
        # Create temporary config
        self.test_config = {
            'users': {
                'testuser': '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08'  # sha256 of 'testpass'
            }
        }
        
        # Clean up after tests
        self.original_config_path = 'aidesk_config.json'
        self.original_sessions_path = 'aidesk_sessions.json'
        self.backup_files = {}
        
        # Backup existing files
        for path in [self.original_config_path, self.original_sessions_path]:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    self.backup_files[path] = f.read()
    
    def tearDown(self):
        # Restore original files
        for path, content in self.backup_files.items():
            with open(path, 'w') as f:
                f.write(content)
        
        # Remove test files if any remain
        for path in [self.original_config_path, self.original_sessions_path]:
            if not path in self.backup_files and os.path.exists(path):
                os.remove(path)
    
    @patch('aidesk.api_handlers.auth.get_config')
    @patch('aidesk.api_handlers.auth.save_sessions')
    def test_successful_login(self, mock_save, mock_get_config):
        mock_get_config.return_value = self.test_config
        
        # Test login data
        post_data = b'username=testuser&password=testpass'
        
        # Call handler
        handle_login_api(self.handler, post_data)
        
        # Check that we got a 200 response with success
        self.handler.send_response.assert_called_with(200)
        self.assertTrue(any('Set-Cookie' in h[0] for h in self.handler.send_header.call_args_list))
    
    @patch('aidesk.api_handlers.auth.get_config')
    def test_failed_login(self, mock_get_config):
        mock_get_config.return_value = self.test_config
        
        # Test invalid password
        post_data = b'username=testuser&password=wrongpass'
        
        # Call handler
        handle_login_api(self.handler, post_data)
        
        # Check that we got an error response
        self.handler.send_json_response.assert_called_with(
            {'success': False, 'message': 'Invalid username or password'},
            401
        )

if __name__ == '__main__':
    unittest.main()
