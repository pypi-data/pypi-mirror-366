# aidesk

A simple web service to generate files via API, with a CLI to start the service.

## Features

- Web service based on Python's built-in `http.server`
- API endpoint to generate files from text content
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

## API

### Generate File

**POST /generate-file**

Parameters:
- `filename`: Name of the file to generate
- `content`: Multi-line text content for the file

Example with curl:
curl -X POST http://localhost:8000/generate-file \
  -d "filename=example.txt&content=First line%0ASecond line%0AThird line"
Response (JSON):{
  "success": true,
  "message": "File generated successfully",
  "file_path": "generated_files/example.txt"
}
## License

MIT
