import unittest
import os
import tempfile
from unittest.mock import Mock, patch
from aidesk.api_handlers.file_handling import handle_generate_file, handle_upload_file

class TestFileHandlers(unittest.TestCase):
    
    def setUp(self):
        # Create mock handler
        self.handler = Mock()
        self.handler.send_json_response = Mock()
        
        # Create temporary directories
        self.generated_dir = tempfile.TemporaryDirectory()
        self.uploads_dir = tempfile.TemporaryDirectory()
        
        # Patch directories
        self.patcher_generated = patch('aidesk.api_handlers.file_handling.os.path.join', 
                                      side_effect=lambda *args: os.path.join(self.generated_dir.name, args[-1]) 
                                      if args[0] == 'generated_files' 
                                      else os.path.join(self.uploads_dir.name, args[-1]))
        self.patcher_generated.start()
    
    def tearDown(self):
        # Clean up
        self.generated_dir.cleanup()
        self.uploads_dir.cleanup()
        self.patcher_generated.stop()
    
    def test_handle_generate_file_success(self):
        # Test data
        post_data = b'filename=test.txt&content=Line+1%0ALine+2'
        
        # Call handler
        handle_generate_file(self.handler, post_data)
        
        # Check response
        self.handler.send_json_response.assert_called_with({
            'success': True,
            'message': 'File generated successfully',
            'file_path': os.path.join(self.generated_dir.name, 'test.txt')
        })
        
        # Check file was created with correct content
        with open(os.path.join(self.generated_dir.name, 'test.txt'), 'r') as f:
            content = f.read()
            self.assertEqual(content, 'Line 1\nLine 2')
    
    def test_handle_generate_file_missing_params(self):
        # Missing filename
        post_data = b'content=Test+content'
        handle_generate_file(self.handler, post_data)
        self.handler.send_json_response.assert_called_with(
            {'success': False, 'message': 'Filename and content are required'},
            400
        )
    
    @patch('aidesk.api_handlers.file_handling.open')
    def test_handle_generate_file_error(self, mock_open):
        # Force an error
        mock_open.side_effect = Exception('Test error')
        post_data = b'filename=error.txt&content=Test'
        
        handle_generate_file(self.handler, post_data)
        self.handler.send_json_response.assert_called_with(
            {'success': False, 'message': 'Error generating file: Test error'},
            500
        )

if __name__ == '__main__':
    unittest.main()
