# DeepSeek-OCR-CPU: Complete Guide

A powerful, CPU-optimized Optical Character Recognition (OCR) system based on DeepSeek OCR. This toolkit provides both command-line tools and a REST API for extracting text, images, tables, and structured content from documents and images.

**Table of Contents:**
- [Features](#features)
- [Quick Start](#quick-start)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [API Server](#api-server)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

---

## Features

✅ **CPU-First Design** - Optimized to run entirely on CPU without CUDA or GPU  
✅ **Multi-Format Support** - Process images (PNG, JPG, etc.) and PDFs  
✅ **Advanced Text Extraction** - Extract paragraphs, titles, and equations with bounding boxes  
✅ **Element Extraction** - Separate extraction of tables, figures, and text blocks  
✅ **REST API** - Deploy as a microservice with FastAPI  
✅ **Docker Support** - Ready-to-deploy containerized setup  
✅ **High Accuracy** - State-of-the-art OCR powered by DeepSeek's vision model  

---

## Quick Start

### Option 1: Command-Line (Fastest for Testing)

```bash
# 1. Run the setup script (one-time)
bash setup/setup_cpu_env.sh

# 2. Activate environment
source .venv/bin/activate

# 3. Test with an image
python image_demo.py

# 4. Test with a PDF
python pdf_demo.py
```

### Option 2: REST API with Docker (Recommended for Production)

⚠️ **Important:** Docker requires the model files to be downloaded first. You **must** run the setup script before Docker.

```bash
# 1. Download model and dependencies (one-time setup)
bash setup/setup_cpu_env.sh

# 2. Build and start the Docker service
docker-compose up -d

# 3. Verify it's running (may take 30-60s on first startup)
curl http://localhost:8000/api/v1/health

# 4. Process a file via API
curl -X POST http://localhost:8000/api/v1/ocr/image \
  -F "file=@your_image.png"

# 5. View logs (optional)
docker-compose logs -f

# 6. Stop the service
docker-compose down
```

**Why the setup script first?**
- The `setup_cpu_env.sh` script downloads the ~7GB model to `model_data/deepseek-ai/DeepSeek-OCR/`
- Docker mounts this directory as a volume (read-only) to avoid re-downloading inside the container
- This saves time and bandwidth on subsequent runs

---

## System Requirements

- **OS:** Linux, macOS, or Windows (WSL2 recommended)
- **Python:** 3.10 or 3.12 (tested with both)
- **RAM:** Minimum 4GB (8GB+ recommended)
- **Storage:** ~7GB for model weights + space for outputs
- **CPU:** Multi-core recommended (Intel/AMD/Apple Silicon supported)

### Optional Dependencies
- Docker & Docker Compose (for API deployment)
- Git (for cloning)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/shamitv/DeepSeek-OCR-CPU.git
cd DeepSeek-OCR-CPU
```

### Step 2: Run the Setup Script

This automated script handles everything:

```bash
bash setup/setup_cpu_env.sh
```

**What it does:**
- Creates a Python virtual environment (`.venv/`)
- Installs PyTorch CPU version
- Installs all project dependencies
- Downloads the DeepSeek OCR model (~7GB)
- Applies CPU patches to the model
- Verifies the installation

**Using a custom environment path:**
```bash
bash setup/setup_cpu_env.sh ~/.virtualenvs/deepseek-ocr
```

### Step 3: Verify Installation

```bash
# Activate the environment
source .venv/bin/activate

# Run a quick test
python -c "from inference import process_image; print('✓ Installation successful')"
```

---

## Usage

### Working with Images

#### Basic Image OCR

```bash
source .venv/bin/activate
python image_demo.py
```

This processes all supported images in `test_files/images/` and outputs results to `test_files/images/outputs/`.

#### Python API

```python
from inference import process_image

# Process a single image
result = process_image(
    image_path="path/to/image.png",
    output_dir="/tmp/results"
)

print(result)  # Extracted markdown text
```

---

### Working with PDFs

#### Basic PDF OCR

```bash
source .venv/bin/activate
python pdf_demo.py
```

This processes the first PDF in `test_files/pdf/` and saves results in a `test_files/pdf/{filename}_outputs/` folder.

#### Process a Specific PDF

```bash
python pdf_demo.py /path/to/document.pdf
```

#### Python API

```python
from inference import process_pdf

# Process an entire PDF
result = process_pdf(
    pdf_path="path/to/document.pdf",
    output_dir="/tmp/results",
    max_pages=None  # Process all pages
)

print(result)  # Extracted markdown text
```

---

### Enhanced Extraction (Advanced)

For applications needing structured data, individual element images, and detailed metadata:

#### Enhanced PDF Processing

```bash
source .venv/bin/activate
python pdf_demo_enhanced.py /path/to/document.pdf
```

**Output includes:**
- Individual images for each element (titles, paragraphs, tables, figures)
- Type-specific bounding box overlays
- JSON metadata with element locations
- Full document structure

#### Python API

```python
from inference import process_pdf_enhanced

result = process_pdf_enhanced(
    pdf_path="document.pdf",
    output_dir="/tmp/results",
    generate_overlays=True,  # Create visual overlays
    save_elements=True       # Save individual elements
)

# Access structured output
print(result['text'])           # Full markdown
print(result['elements'])       # Element details
print(result['document_structure'])  # Overall structure
```

---

## API Server

### Before You Start: Model Download Required

The Docker API requires the model files to already exist. **You must run the setup script first:**

```bash
# One-time setup (downloads ~7GB model)
bash setup/setup_cpu_env.sh

# Docker will use the model_data/ volume
```

Once the model is downloaded, Docker will not re-download it on subsequent runs.

### Starting the API

#### With Docker Compose (Recommended)

**Option A: Automatic Setup & Start (Easiest)**

```bash
# This script checks for the model, runs setup if needed, and starts Docker
bash start_docker.sh

# That's it! The API will be ready at http://localhost:8000/docs
```

**Option B: Manual Setup & Start**

```bash
# First run setup (downloads ~7GB model)
bash setup/setup_cpu_env.sh

# Then start the service
docker-compose up -d

# View logs (takes 30-60s to load model on first startup)
docker-compose logs -f deepseek-ocr-api

# Stop the service
docker-compose down
```

#### Without Docker (Development)

```bash
# First run setup
bash setup/setup_cpu_env.sh

# Then start the server
source .venv/bin/activate
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Health & Information

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get model information
curl http://localhost:8000/api/v1/info
```

#### Image Processing

```bash
curl -X POST http://localhost:8000/api/v1/ocr/image \
  -F "file=@image.png" \
  -F "save_output=true"
```

**Parameters:**
- `file` (required): Image file (PNG, JPG, etc.)
- `save_output` (optional): Save results to disk (default: false)

**Response:**
```json
{
  "success": true,
  "text": "Extracted text content...",
  "processing_time": 2.45
}
```

#### PDF Processing

```bash
curl -X POST http://localhost:8000/api/v1/ocr/pdf \
  -F "file=@document.pdf" \
  -F "max_pages=5" \
  -F "save_output=true"
```

**Parameters:**
- `file` (required): PDF file
- `max_pages` (optional): Limit number of pages to process
- `save_output` (optional): Save results to disk (default: false)

**Response:**
```json
{
  "success": true,
  "text": "Extracted text from all pages...",
  "num_pages": 5,
  "processing_time": 12.34,
  "pages": [
    {"page_number": 1, "text": "Page 1 content..."},
    {"page_number": 2, "text": "Page 2 content..."}
  ]
}
```

#### Enhanced PDF Processing

```bash
curl -X POST http://localhost:8000/api/v1/ocr/pdf/enhanced \
  -F "file=@document.pdf" \
  -F "generate_overlays=true" \
  -F "save_elements=true"
```

**Parameters:**
- `file` (required): PDF file
- `generate_overlays` (optional): Create visual element overlays
- `save_elements` (optional): Save individual element images
- `max_pages` (optional): Limit pages

**Response:**
```json
{
  "success": true,
  "text": "Full document text...",
  "num_pages": 10,
  "num_elements": 45,
  "elements": [
    {
      "type": "title",
      "text": "Document Title",
      "page": 1,
      "bbox": [10, 20, 200, 50]
    }
  ],
  "processing_time": 15.67
}
```

### API Documentation

Once the API is running, access interactive documentation at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Python Client Example

```python
import requests

def process_with_api(file_path):
    url = "http://localhost:8000/api/v1/ocr/image"
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Text: {result['text']}")
        print(f"Time: {result['processing_time']:.2f}s")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

process_with_api("image.png")
```

### JavaScript/Node.js Client Example

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function processWithAPI(filePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));
  form.append('save_output', 'true');

  try {
    const response = await axios.post(
      'http://localhost:8000/api/v1/ocr/image',
      form,
      { headers: form.getHeaders() }
    );

    console.log('Success:', response.data.success);
    console.log('Text:', response.data.text);
    console.log('Time:', response.data.processing_time, 'seconds');
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

processWithAPI('image.png');
```

---

## Advanced Features

### Custom Python Integration

Import functions for use in your own projects:

```python
from inference import (
    process_image,
    process_pdf,
    pdf_to_images,
    process_image_enhanced,
    process_pdf_enhanced
)

# Single image
result = process_image("path/to/image.png")

# PDF with metrics
from inference import process_pdf_with_metrics
result, metrics = process_pdf_with_metrics("document.pdf")
print(f"Processed {metrics['num_pages']} pages in {metrics['time']:.2f}s")

# Convert PDF to images first
images = pdf_to_images("document.pdf")
for img_array in images:
    # Process individual image
    text = process_image(img_array)
```

### Performance Metrics

Track processing performance:

```python
from inference import process_image_with_metrics

text, metrics = process_image_with_metrics("image.png")
print(f"Time: {metrics['inference_time']:.2f}s")
print(f"Memory: {metrics['memory_usage_mb']:.1f}MB")
```

### Batch Processing

Process multiple files:

```bash
#!/bin/bash
source .venv/bin/activate

for file in test_files/images/*.png; do
    echo "Processing $file..."
    python -c "from inference import process_image; process_image('$file')"
done
```

---

## Troubleshooting

### Installation Issues

**Problem: Setup script fails with permission error**
```bash
# Solution: Make script executable
chmod +x setup/setup_cpu_env.sh
bash setup/setup_cpu_env.sh
```

**Problem: Model download fails (network timeout)**
```bash
# Solution: Download model manually and place in model_data/
mkdir -p model_data/deepseek-ai
cd model_data/deepseek-ai
# Then place the downloaded model there
```

### Runtime Issues

**Problem: "ModuleNotFoundError: No module named 'inference'"**
```bash
# Solution: Activate virtual environment
source .venv/bin/activate
# Then run your script
```

**Problem: Out of memory (OOM) error**
```bash
# Solution: Process fewer pages at once
python pdf_demo.py document.pdf  # Default: processes all pages

# Or limit pages in code:
from inference import process_pdf
process_pdf("document.pdf", max_pages=5)
```

**Problem: Docker build fails**
```bash
# Solution: Clear cache and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### API Issues

**Problem: "Connection refused" when accessing API**
```bash
# Check if container is running
docker ps

# Check logs
docker-compose logs deepseek-ocr-api

# Restart service
docker-compose restart
```

**Problem: Slow API responses**
- Check resource allocation in `docker-compose.yml`
- Reduce `DEEPSEEK_OCR_WORKERS` if memory is limited
- Process fewer pages per request

### Performance Optimization

1. **CPU Configuration**
   - Adjust worker count in `docker-compose.yml` (default: 1)
   - More workers = faster but uses more memory

2. **Memory Usage**
   - Process PDFs in batches with `max_pages`
   - Monitor with `docker stats`

3. **Processing Speed**
   - GPU acceleration not available (CPU-only by design)
   - Multi-page processing is sequential

---

## Project Structure

```
├── api/                      # FastAPI application
│   ├── main.py              # API endpoints
│   ├── models.py            # Request/response schemas
│   ├── config.py            # Configuration
│   └── README.md            # API documentation
├── inference/               # Core OCR engine
│   ├── image.py             # Image processing
│   ├── pdf.py               # PDF processing
│   ├── model_loader.py      # Model initialization
│   ├── extraction/          # Element extraction
│   ├── structuring/         # Document structure
│   └── linking/             # Element linking
├── test_files/              # Test data
│   ├── images/              # Sample images
│   └── pdf/                 # Sample PDFs
├── model_patch/             # CPU optimization patches
├── setup/                   # Installation scripts
│   └── setup_cpu_env.sh     # One-time setup
├── Dockerfile               # Container definition
├── docker-compose.yml       # Multi-container setup
├── image_demo.py            # Image processing demo
├── pdf_demo.py              # PDF processing demo
├── pdf_demo_enhanced.py     # Enhanced extraction demo
├── test_api.py              # API testing script
└── requirements.txt         # Python dependencies
```

---

## Configuration

### Environment Variables (Docker)

Edit `docker-compose.yml` to customize:

```yaml
environment:
  - DEEPSEEK_OCR_DEBUG=false              # Enable debug logging
  - DEEPSEEK_OCR_WORKERS=1                # API worker threads
  - DEEPSEEK_OCR_MAX_UPLOAD_SIZE=52428800 # Max file size (50MB)
  - DEEPSEEK_OCR_DEVICE=cpu               # Processing device
  - DEEPSEEK_OCR_CORS_ORIGINS=["*"]       # CORS settings
```

### Resource Limits

Adjust CPU/Memory allocation in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # Maximum CPU cores
      memory: 8G     # Maximum memory
```

---

## Testing

### Test the Command-Line Tools

```bash
source .venv/bin/activate

# Test image processing
python image_demo.py

# Test PDF processing
python pdf_demo.py

# Test enhanced extraction
python pdf_demo_enhanced.py test_files/pdf/*.pdf
```

### Test the API

```bash
# Using the provided test script
source .venv/bin/activate
python test_api.py

# Or manually with curl
curl http://localhost:8000/api/v1/health
```

---

## Contributing

Found a bug or have an improvement? Please open an issue or submit a pull request.

## License

This project is built on DeepSeek OCR. See `LICENSE` for details.

---

## Support

- **Issues & Questions:** Open a GitHub issue
- **API Documentation:** http://localhost:8000/docs (when running)
- **Original DeepSeek Docs:** See `README-source.md`

---

## Citation

If you use this toolkit in research, please cite:

```bibtex
@inproceedings{deepseek-ocr,
  title={DeepSeek-OCR: Towards a Unified Vision Model for OCR},
  author={DeepSeek},
  year={2024}
}
```

---

**Last Updated:** November 2025  
**Version:** 1.0  
**Status:** Production Ready
