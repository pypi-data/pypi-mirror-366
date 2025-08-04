import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs

class AideskHandler(http.server.BaseHTTPRequestHandler):
    """处理aidesk的HTTP请求"""
    
    def _set_headers(self, status_code=200, content_type='text/html'):
        """设置HTTP响应头"""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/':
            # 主页 - 展示API文档
            self._set_headers()
            html = """
            <html>
            <head>
                <title>aidesk API</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                    .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                    h1 { color: #333; }
                    h2 { color: #555; }
                </style>
            </head>
            <body>
                <h1>aidesk API</h1>
                <p>Simple web service to generate files from text content.</p>
                
                <div class="endpoint">
                    <h2>Generate File</h2>
                    <p><strong>POST /generate-file</strong></p>
                    <p>Parameters:</p>
                    <ul>
                        <li><code>filename</code> - Name of the file to generate</li>
                        <li><code>content</code> - Multi-line text content for the file</li>
                    </ul>
                    <p>Example request:</p>
                    <pre>
curl -X POST http://localhost:8000/generate-file \
  -d "filename=example.txt&content=Line 1%0ALine 2%0ALine 3"
                    </pre>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            # 未知路径
            self._set_headers(404)
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        """处理POST请求"""
        if self.path == '/generate-file':
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            
            # 验证参数
            if 'filename' not in params or 'content' not in params:
                self._set_headers(400, 'application/json')
                response = {
                    'success': False,
                    'message': 'Missing parameters. Need both filename and content.',
                    'file_path': None
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            
            filename = params['filename'][0]
            content = params['content'][0]
            
            try:
                # 确保生成文件的目录存在
                if not os.path.exists('generated_files'):
                    os.makedirs('generated_files', exist_ok=True)
                
                # 生成文件路径
                file_path = os.path.join('generated_files', filename)
                
                # 写入文件内容
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # 返回成功响应
                self._set_headers(200, 'application/json')
                response = {
                    'success': True,
                    'message': f'File generated successfully',
                    'file_path': file_path
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                # 处理错误
                self._set_headers(500, 'application/json')
                response = {
                    'success': False,
                    'message': f'Error generating file: {str(e)}',
                    'file_path': None
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            # 未知路径
            self._set_headers(404)
            self.wfile.write(b'Not Found')

def run_server(host='localhost', port=8000, debug=False):
    """启动web服务器"""
    handler = AideskHandler
    with socketserver.TCPServer((host, port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer is shutting down...")
            httpd.shutdown()
