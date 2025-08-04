import os
import json
import uuid
from urllib.parse import parse_qs
import re

def handle_generate_file(handler, post_data):
    """Handle file generation API request"""
    try:
        # Parse form data
        data = parse_qs(post_data.decode('utf-8'))
        filename = data.get('filename', [None])[0]
        content = data.get('content', [None])[0]
        
        if not filename or not content:
            handler.send_json_response({
                'success': False,
                'message': 'Filename and content are required'
            }, 400)
            return
        
        # Sanitize filename
        filename = re.sub(r'[^a-zA-Z0-9_.-]', '', filename)
        file_path = os.path.join('generated_files', filename)
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        handler.send_json_response({
            'success': True,
            'message': 'File generated successfully',
            'file_path': file_path
        })
        
    except Exception as e:
        handler.send_json_response({
            'success': False,
            'message': f'Error generating file: {str(e)}'
        }, 500)

def handle_upload_file(handler, post_data, headers):
    """Handle file upload API request"""
    try:
        content_type = headers.get('Content-Type', '')
        if not content_type.startswith('multipart/form-data'):
            handler.send_json_response({
                'success': False,
                'message': 'Content-Type must be multipart/form-data'
            }, 400)
            return
        
        # Extract boundary
        boundary = content_type.split('boundary=')[1].encode('utf-8')
        parts = post_data.split(boundary)
        
        # Find file part
        file_data = None
        file_name = None
        
        for part in parts:
            if b'filename=' in part:
                # Extract filename
                filename_match = re.search(rb'filename="(.*?)"', part)
                if filename_match:
                    file_name = filename_match.group(1).decode('utf-8')
                    # Sanitize filename
                    file_name = re.sub(r'[^a-zA-Z0-9_.-]', '', file_name)
                
                # Extract file content
                content_start = part.find(b'\r\n\r\n') + 4
                content_end = part.rfind(b'\r\n--')
                if content_start < content_end:
                    file_data = part[content_start:content_end]
        
        if not file_data or not file_name:
            handler.send_json_response({
                'success': False,
                'message': 'No file data received'
            }, 400)
            return
        
        # Save file
        file_path = os.path.join('uploads', file_name)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        handler.send_json_response({
            'success': True,
            'message': 'File uploaded successfully',
            'file_path': file_path
        })
        
    except Exception as e:
        handler.send_json_response({
            'success': False,
            'message': f'Error uploading file: {str(e)}'
        }, 500)
