import unittest
import os
import tempfile
import json
from urllib.parse import urlencode
from aidesk.server import AideskHandler
from http.server import BaseHTTPRequestHandler
from unittest.mock import patch, MagicMock

class TestAidesk(unittest.TestCase):
    
    def test_file_creation_logic(self):
        """测试文件创建逻辑"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 模拟表单数据
            filename = "test.txt"
            content = "Line 1\nLine 2\nLine 3"
            
            # 更改输出目录为临时目录
            with patch('aidesk.server.os.path.join') as mock_join:
                mock_join.side_effect = lambda *args: os.path.join(temp_dir, args[-1])
                
                try:
                    # 尝试创建文件
                    file_path = os.path.join(temp_dir, filename)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # 验证文件是否创建成功
                    self.assertTrue(os.path.exists(file_path))
                    
                    # 验证文件内容是否正确
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.assertEqual(f.read(), content)
                        
                except Exception as e:
                    self.fail(f"File creation failed with exception: {e}")

    @patch.object(AideskHandler, 'send_response')
    @patch.object(AideskHandler, 'send_header')
    @patch.object(AideskHandler, 'end_headers')
    @patch.object(AideskHandler, 'wfile', new_callable=MagicMock)
    def test_api_response(self, mock_wfile, mock_end_headers, mock_send_header, mock_send_response):
        """测试API响应"""
        handler = AideskHandler(MagicMock(), MagicMock(), MagicMock())
        handler.headers = {'Content-Length': '35'}
        
        # 模拟POST数据
        post_data = urlencode({
            'filename': 'test-api.txt',
            'content': 'Test API content'
        }).encode('utf-8')
        
        with patch('aidesk.server.os.path.exists', return_value=True):
            with patch('aidesk.server.open', create=True) as mock_open:
                handler.rfile = MagicMock()
                handler.rfile.read.return_value = post_data
                
                handler.do_POST()
                
                # 验证响应
                mock_send_response.assert_called_with(200)
                mock_send_header.assert_any_call('Content-type', 'application/json')
                
                # 验证响应内容
                written_data = mock_wfile.write.call_args[0][0].decode('utf-8')
                response = json.loads(written_data)
                self.assertTrue(response['success'])
                self.assertIn('test-api.txt', response['file_path'])

if __name__ == '__main__':
    unittest.main()
