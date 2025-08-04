from ..utils import load_template

def handle_index(handler, is_authenticated):
    """Handle the main index page"""
    # Load template and replace placeholders
    template = load_template('index.html')
    auth_status = "Logged in" if is_authenticated else "Not logged in"
    login_logout_link = "/logout" if is_authenticated else "/login"
    login_logout_text = "Logout" if is_authenticated else "Login"
    
    content = template.replace('{{ auth_status }}', auth_status)
    content = content.replace('{{ login_logout_link }}', login_logout_link)
    content = content.replace('{{ login_logout_text }}', login_logout_text)
    
    handler.send_response(200)
    handler.send_header('Content-type', 'text/html')
    handler.end_headers()
    handler.wfile.write(content.encode('utf-8'))
