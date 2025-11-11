# Multi-stage Dockerfile for DeepSeek OCR CPU Service
# Stage 1: Base image with dependencies
FROM python:3.10-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Stage 2: Dependencies
FROM base AS dependencies

# Copy requirements file
COPY requirements.txt ./

# Install PyTorch CPU version FIRST (matching setup_cpu_env.sh)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.6.0+cpu torchvision==0.21.0+cpu

# Install huggingface-hub for model loading
RUN pip install --no-cache-dir huggingface-hub

# Install all other project requirements
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM dependencies AS application

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /tmp/deepseek_ocr/outputs && \
    mkdir -p /app/model_data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
