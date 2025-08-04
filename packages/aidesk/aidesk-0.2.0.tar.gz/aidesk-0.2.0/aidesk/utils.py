import os
import json
import hashlib
from pathlib import Path

# Configuration
CONFIG_PATH = 'aidesk_config.json'
SESSIONS_PATH = 'aidesk_sessions.json'
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def load_template(template_name):
    """Load an HTML template file"""
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"<html><body>Template {template_name} not found</body></html>"

def get_config():
    """Load configuration or create default if not exists"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Create default config with sample user (username: admin, password: admin)
    default_config = {
        'users': {
            'admin': hashlib.sha256('admin'.encode()).hexdigest()
        }
    }
    
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2)
    
    return default_config

def load_sessions():
    """Load sessions from file"""
    if os.path.exists(SESSIONS_PATH):
        try:
            with open(SESSIONS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_sessions(sessions):
    """Save sessions to file"""
    with open(SESSIONS_PATH, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, indent=2)

def get_session_id(headers):
    """Extract session ID from cookies"""
    if 'Cookie' in headers:
        cookies = headers['Cookie'].split(';')
        for cookie in cookies:
            if cookie.strip().startswith('session_id='):
                return cookie.split('=')[1]
    return None

def validate_session(session_id):
    """Check if session is valid"""
    if not session_id:
        return False
    
    sessions = load_sessions()
    return session_id in sessions and sessions[session_id].get('valid', False)
