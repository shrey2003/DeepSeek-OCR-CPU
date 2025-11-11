"""Configuration for the FastAPI OCR service."""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API settings
    app_name: str = "DeepSeek OCR API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1  # Keep at 1 for model loading
    
    # File upload settings
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    allowed_image_extensions: set = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
    allowed_pdf_extensions: set = {".pdf"}
    
    # Processing settings
    temp_dir: Path = Path("/tmp/deepseek_ocr")
    output_dir: Path = Path("/tmp/deepseek_ocr/outputs")
    cleanup_temp_files: bool = True
    
    # Model settings
    model_path: Optional[str] = None  # Will use default from inference module
    device: str = "cpu"
    
    # CORS settings
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    class Config:
        env_prefix = "DEEPSEEK_OCR_"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.temp_dir.mkdir(parents=True, exist_ok=True)
settings.output_dir.mkdir(parents=True, exist_ok=True)
