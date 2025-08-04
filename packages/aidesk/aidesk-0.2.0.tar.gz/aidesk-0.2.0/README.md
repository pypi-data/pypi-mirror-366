# aidesk

A simple web service with file operations and authentication.

## Features

- Web service based on Python's built-in `http.server`
- User authentication (login/logout)
- API endpoint to generate files from text content
- API endpoint to upload files
- CLI to start the service with custom host and port
- Simple web interface showing API documentation

## Installation
pip install aidesk
## Usage

Start the web service:
# Default host (localhost) and port (8000)
aidesk

# Custom host and port
aidesk --host 0.0.0.0 --port 8080

# Debug mode
aidesk --debug
Once the service is running, you can access the API documentation at http://localhost:8000

Default credentials:
- Username: admin
- Password: admin

## API

### Authentication

**POST /api/login**

Parameters:
- `username`: Your username
- `password`: Your password

Example:curl -X POST http://localhost:8000/api/login \
  -d "username=admin&password=admin"
### Generate File

**POST /api/generate-file** (Requires authentication)

Parameters:
- `filename`: Name of the file to generate
- `content`: Multi-line text content for the file

Example:curl -X POST http://localhost:8000/api/generate-file \
  -b "session_id=your_session_id" \
  -d "filename=example.txt&content=First line%0ASecond line%0AThird line"
### Upload File

**POST /api/upload-file** (Requires authentication)

Parameters:
- File data as multipart/form-data

Example:curl -X POST http://localhost:8000/api/upload-file \
  -b "session_id=your_session_id" \
  -F "file=@localfile.txt"
## License

MIT
