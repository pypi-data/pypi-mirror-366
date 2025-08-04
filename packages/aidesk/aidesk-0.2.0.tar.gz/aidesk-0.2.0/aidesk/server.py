import http.server
import socketserver
import os
from urllib.parse import urlparse, parse_qs
import json
from .api_handlers import home, auth, file_handling
from .utils import load_template, get_session_id, validate_session

class AideskHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        # Check authentication status
        session_id = get_session_id(self.headers)
        is_authenticated = validate_session(session_id)
        
        # Route to appropriate handler
        if path == '/':
            home.handle_index(self, is_authenticated)
        elif path == '/login':
            auth.handle_login_form(self)
        elif path == '/logout':
            auth.handle_logout(self)
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Get content length
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Check authentication status for protected routes
        session_id = get_session_id(self.headers)
        is_authenticated = validate_session(session_id)
        
        # Route to appropriate handler
        if path == '/api/login':
            auth.handle_login_api(self, post_data)
        elif path == '/api/generate-file':
            if is_authenticated:
                file_handling.handle_generate_file(self, post_data)
            else:
                self.send_json_response({"success": False, "message": "Authentication required"}, 401)
        elif path == '/api/upload-file':
            if is_authenticated:
                file_handling.handle_upload_file(self, post_data, self.headers)
            else:
                self.send_json_response({"success": False, "message": "Authentication required"}, 401)
        else:
            self.send_error(404, "Not Found")

    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def run_server(host, port, debug=False):
    handler = AideskHandler
    with socketserver.TCPServer((host, port), handler) as httpd:
        print(f'Starting aidesk server on {host}:{port}...')
        if debug:
            print('Debug mode enabled')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nServer stopped.')
            httpd.shutdown()
