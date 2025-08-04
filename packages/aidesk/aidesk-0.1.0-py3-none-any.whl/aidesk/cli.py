import argparse
import os
from .server import run_server

def main():
    parser = argparse.ArgumentParser(description='Start the aidesk web service.')
    parser.add_argument('--host', type=str, default='localhost', 
                      help='Host to bind the server (default: localhost)')
    parser.add_argument('--port', type=int, default=8000, 
                      help='Port to run the server (default: 8000)')
    parser.add_argument('--debug', action='store_true', 
                      help='Run in debug mode')
    
    args = parser.parse_args()
    
    # 创建生成文件的目录
    if not os.path.exists('generated_files'):
        os.makedirs('generated_files', exist_ok=True)
    
    print(f"Starting aidesk web service on {args.host}:{args.port}")
    print(f"API documentation available at http://{args.host}:{args.port}")
    run_server(args.host, args.port, args.debug)

if __name__ == '__main__':
    main()
