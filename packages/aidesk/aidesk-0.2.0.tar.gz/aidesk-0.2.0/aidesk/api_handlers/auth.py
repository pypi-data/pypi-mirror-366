import json
import hashlib
import uuid
from urllib.parse import parse_qs
from ..utils import load_template, save_sessions, load_sessions, get_config

# In-memory session storage
sessions = load_sessions()

def handle_login_form(handler):
    """Handle the login form page"""
    template = load_template('login.html')
    handler.send_response(200)
    handler.send_header('Content-type', 'text/html')
    handler.end_headers()
    handler.wfile.write(template.encode('utf-8'))

def handle_login_api(handler, post_data):
    """Handle the login API request"""
    # Parse form data
    data = parse_qs(post_data.decode('utf-8'))
    username = data.get('username', [None])[0]
    password = data.get('password', [None])[0]
    
    # Get valid credentials from config
    config = get_config()
    valid_users = config.get('users', {})
    
    # Check credentials
    if username in valid_users:
        # Hash password for comparison
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if hashed_password == valid_users[username]:
            # Create session
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                'username': username,
                'valid': True
            }
            save_sessions(sessions)
            
            # Set session cookie
            handler.send_response(200)
            handler.send_header('Content-type', 'application/json')
            handler.send_header('Set-Cookie', f'session_id={session_id}; Path=/')
            handler.end_headers()
            handler.wfile.write(json.dumps({
                'success': True,
                'message': 'Login successful'
            }).encode('utf-8'))
            return
    
    # Invalid credentials
    handler.send_json_response({
        'success': False,
        'message': 'Invalid username or password'
    }, 401)

def handle_logout(handler):
    """Handle logout"""
    global sessions
    
    # Get session ID from cookie
    session_id = None
    if 'Cookie' in handler.headers:
        cookies = handler.headers['Cookie'].split(';')
        for cookie in cookies:
            if cookie.strip().startswith('session_id='):
                session_id = cookie.split('=')[1]
    
    # Remove session if exists
    if session_id in sessions:
        del sessions[session_id]
        save_sessions(sessions)
    
    # Redirect to home
    handler.send_response(302)
    handler.send_header('Location', '/')
    handler.end_headers()
