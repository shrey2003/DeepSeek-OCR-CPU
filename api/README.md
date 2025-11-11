# DeepSeek OCR API

FastAPI-based REST API service for DeepSeek OCR on CPU.

## Quick Start

### Using Docker Compose (Recommended)

1. **Build and start the service:**
   ```bash
   docker-compose up -d
   ```

2. **Check the logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/api/v1/health

4. **Stop the service:**
   ```bash
   docker-compose down
   ```

### Using Docker Directly

1. **Build the image:**
   ```bash
   docker build -t deepseek-ocr-api .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name deepseek-ocr-api \
     -p 8000:8000 \
     -v $(pwd)/model_data:/app/model_data:ro \
     -v $(pwd)/outputs:/tmp/deepseek_ocr/outputs \
     deepseek-ocr-api
   ```

### Local Development (without Docker)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-api.txt
   ```

2. **Run the server:**
   ```bash
   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### Health & Info

- `GET /api/v1/health` - Health check
- `GET /api/v1/info` - Model information

### OCR Processing

- `POST /api/v1/ocr/image` - Process an image file
- `POST /api/v1/ocr/pdf` - Process a PDF document
- `POST /api/v1/ocr/pdf/enhanced` - Process PDF with enhanced extraction

## Usage Examples

### Using cURL

**Process an image:**
```bash
curl -X POST "http://localhost:8000/api/v1/ocr/image" \
  -F "file=@/path/to/image.png" \
  -F "save_output=true"
```

**Process a PDF:**
```bash
curl -X POST "http://localhost:8000/api/v1/ocr/pdf" \
  -F "file=@/path/to/document.pdf" \
  -F "max_pages=5" \
  -F "save_output=true"
```

**Process PDF with enhanced extraction:**
```bash
curl -X POST "http://localhost:8000/api/v1/ocr/pdf/enhanced" \
  -F "file=@/path/to/document.pdf" \
  -F "generate_overlays=true" \
  -F "save_elements=true"
```

### Using Python

```python
import requests

# Process an image
url = "http://localhost:8000/api/v1/ocr/image"
files = {"file": open("image.png", "rb")}
response = requests.post(url, files=files)
result = response.json()

print(f"Success: {result['success']}")
print(f"Text: {result['text']}")
print(f"Processing time: {result['processing_time']:.2f}s")

# Process a PDF
url = "http://localhost:8000/api/v1/ocr/pdf"
files = {"file": open("document.pdf", "rb")}
params = {"max_pages": 5, "save_output": True}
response = requests.post(url, files=files, data=params)
result = response.json()

print(f"Pages processed: {result['num_pages']}")
print(f"Text: {result['text']}")
```

### Using JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function processImage(imagePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(imagePath));
  form.append('save_output', 'true');

  const response = await axios.post(
    'http://localhost:8000/api/v1/ocr/image',
    form,
    { headers: form.getHeaders() }
  );

  console.log('Success:', response.data.success);
  console.log('Text:', response.data.text);
  console.log('Processing time:', response.data.processing_time);
}

processImage('image.png');
```

## Configuration

Configure the API using environment variables with the `DEEPSEEK_OCR_` prefix:

### Server Settings
- `DEEPSEEK_OCR_HOST` - Server host (default: `0.0.0.0`)
- `DEEPSEEK_OCR_PORT` - Server port (default: `8000`)
- `DEEPSEEK_OCR_WORKERS` - Number of workers (default: `1`)
- `DEEPSEEK_OCR_DEBUG` - Debug mode (default: `false`)

### File Upload Settings
- `DEEPSEEK_OCR_MAX_UPLOAD_SIZE` - Max upload size in bytes (default: `52428800` / 50MB)
- `DEEPSEEK_OCR_CLEANUP_TEMP_FILES` - Cleanup temp files (default: `true`)

### Model Settings
- `DEEPSEEK_OCR_MODEL_PATH` - Custom model path (optional)
- `DEEPSEEK_OCR_DEVICE` - Device to use (default: `cpu`)

### CORS Settings
- `DEEPSEEK_OCR_CORS_ORIGINS` - Allowed origins (default: `["*"]`)

## Docker Compose Configuration

Edit `docker-compose.yml` to customize:

1. **Port mapping:** Change `"8000:8000"` to use a different host port
2. **Resource limits:** Adjust CPU and memory limits under `deploy.resources`
3. **Environment variables:** Add/modify under `environment`
4. **Volumes:** Mount additional directories as needed

## Production Considerations

1. **Security:**
   - Set specific CORS origins instead of `["*"]`
   - Add authentication/authorization middleware
   - Use HTTPS (add nginx reverse proxy)
   - Validate and sanitize file uploads

2. **Performance:**
   - Adjust resource limits based on your hardware
   - Consider using a process manager like gunicorn
   - Implement request rate limiting
   - Add caching for repeated requests

3. **Monitoring:**
   - Add logging aggregation (ELK, Loki)
   - Implement metrics collection (Prometheus)
   - Set up alerts for failures
   - Monitor resource usage

4. **Scalability:**
   - Use a reverse proxy (nginx, traefik)
   - Deploy multiple instances behind a load balancer
   - Consider message queues for async processing
   - Implement result caching (Redis)

## Troubleshooting

**Container won't start:**
- Check logs: `docker-compose logs`
- Verify model_data directory exists and contains the model
- Check port 8000 is not already in use

**Out of memory errors:**
- Increase Docker memory limits
- Reduce `max_pages` parameter when processing PDFs
- Process large documents in batches

**Slow processing:**
- This is CPU-based inference, processing is slower than GPU
- Consider processing in background with task queue
- Implement pagination for large documents

**Model not loading:**
- Ensure model files are in `model_data/` directory
- Check file permissions on mounted volumes
- Verify model path configuration

## API Documentation

Once the service is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These provide interactive API documentation and testing interfaces.
