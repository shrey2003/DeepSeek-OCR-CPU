#!/usr/bin/env bash
# Quick startup script for Docker
# This script ensures the model is downloaded before starting Docker

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="${SCRIPT_DIR}/model_data/deepseek-ai/DeepSeek-OCR"

echo "=================================="
echo "DeepSeek OCR Docker Startup"
echo "=================================="
echo ""

# Check if model exists
if [ -d "${MODEL_DIR}" ] && [ "$(ls -A "${MODEL_DIR}" 2>/dev/null)" ]; then
    echo "✓ Model found at ${MODEL_DIR}"
    echo "  Size: $(du -sh "${MODEL_DIR}" 2>/dev/null | cut -f1)"
else
    echo "✗ Model not found!"
    echo ""
    echo "Running setup script to download model (~7GB)..."
    echo "This may take 10-30 minutes depending on your internet speed."
    echo ""
    
    bash "${SCRIPT_DIR}/setup/setup_cpu_env.sh"
    
    echo ""
    echo "✓ Model downloaded successfully!"
    echo ""
fi

echo ""
echo "Starting Docker container..."
docker-compose up -d

echo ""
echo "Waiting for API to start (may take 30-60s)..."
sleep 5

# Check health
HEALTH_CHECK_RETRIES=12
HEALTH_CHECK_COUNT=0

while [ $HEALTH_CHECK_COUNT -lt $HEALTH_CHECK_RETRIES ]; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo ""
        echo "✓ API is ready!"
        echo ""
        echo "Access points:"
        echo "  - API Docs: http://localhost:8000/docs"
        echo "  - Health: http://localhost:8000/api/v1/health"
        echo ""
        echo "Test with:"
        echo "  curl -X POST http://localhost:8000/api/v1/ocr/image -F 'file=@image.png'"
        echo ""
        echo "To stop: docker-compose down"
        exit 0
    fi
    
    HEALTH_CHECK_COUNT=$((HEALTH_CHECK_COUNT + 1))
    echo "  Waiting for API... (attempt $HEALTH_CHECK_COUNT/$HEALTH_CHECK_RETRIES)"
    sleep 5
done

echo ""
echo "⚠ API took too long to start. Check logs with:"
echo "  docker-compose logs -f deepseek-ocr-api"
exit 1
