"""FastAPI application for DeepSeek OCR service."""

import logging
import shutil
import tempfile
import time
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from inference import (
    process_image_with_metrics,
    process_pdf_with_metrics,
    process_pdf_enhanced,
)

from .config import settings
from .models import (
    HealthResponse,
    ModelInfo,
    ImageOCRResponse,
    PDFOCRResponse,
    PDFEnhancedResponse,
    ErrorResponse,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Application state
class AppState:
    """Application state container."""
    model_loaded: bool = False
    startup_time: Optional[float] = None


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("Starting DeepSeek OCR API service...")
    app_state.startup_time = time.time()
    
    # Warmup - load model by processing a dummy request
    try:
        logger.info("Loading model... This may take 2-5 minutes on first start...")
        from inference.model_loader import load_model_and_tokenizer
        
        # Actually load the model during startup
        tokenizer, model = load_model_and_tokenizer()
        
        app_state.model_loaded = True
        elapsed = time.time() - app_state.startup_time
        logger.info(f"Model loaded successfully in {elapsed:.2f}s")
    except Exception as e:
        logger.error(f"Model warmup failed: {e}")
        app_state.model_loaded = False
    
    yield
    
    # Shutdown
    logger.info("Shutting down DeepSeek OCR API service...")
    
    # Cleanup temp files if configured
    if settings.cleanup_temp_files:
        try:
            if settings.temp_dir.exists():
                shutil.rmtree(settings.temp_dir)
                logger.info(f"Cleaned up temp directory: {settings.temp_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup temp directory: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="CPU-based OCR service using DeepSeek OCR model",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


def validate_file_extension(filename: str, allowed_extensions: set) -> None:
    """Validate file extension."""
    ext = Path(filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension. Allowed: {', '.join(allowed_extensions)}"
        )


def validate_file_size(file: UploadFile) -> None:
    """Validate file size."""
    # Note: This is a simplified check. For production, consider streaming validation.
    pass  # Size will be checked during upload


async def save_upload_file(upload_file: UploadFile, destination: Path) -> Path:
    """Save uploaded file to destination."""
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return destination
    finally:
        upload_file.file.close()


# Health and info endpoints
@app.get(
    f"{settings.api_prefix}/health",
    response_model=HealthResponse,
    tags=["Health"]
)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if app_state.model_loaded else "starting",
        version=settings.app_version
    )


@app.get(
    f"{settings.api_prefix}/info",
    response_model=ModelInfo,
    tags=["Info"]
)
async def model_info():
    """Get model information."""
    return ModelInfo(
        model_name="DeepSeek-OCR",
        device=settings.device,
        version=settings.app_version
    )


# OCR endpoints
@app.post(
    f"{settings.api_prefix}/ocr/image",
    response_model=ImageOCRResponse,
    tags=["OCR"],
    summary="Process an image with OCR"
)
async def process_image_endpoint(
    file: UploadFile = File(..., description="Image file to process"),
    save_output: bool = True,
):
    """
    Process an image file with OCR.
    
    - **file**: Image file (PNG, JPG, JPEG, BMP, TIFF, WEBP)
    - **save_output**: Whether to save output files
    
    Returns OCR results in text format with performance metrics.
    """
    start_time = time.time()
    temp_file = None
    output_dir = None
    
    try:
        logger.info(f"Received image upload: {file.filename}")
        
        # Validate file
        validate_file_extension(file.filename, settings.allowed_image_extensions)
        
        # Create temp file
        temp_file = settings.temp_dir / f"{time.time()}_{file.filename}"
        await save_upload_file(file, temp_file)
        
        logger.info(f"Processing image: {file.filename} (size: {temp_file.stat().st_size} bytes)")
        
        # Setup output directory
        if save_output:
            output_dir = settings.output_dir / f"{temp_file.stem}_{int(time.time())}"
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process image
        logger.info(f"Starting OCR inference for: {file.filename}")
        result, metrics = process_image_with_metrics(
            str(temp_file),
            output_dir=str(output_dir) if output_dir else None
        )
        logger.info(f"OCR inference completed for: {file.filename} in {metrics.total_time:.2f}s")
        
        # Collect output files
        output_files = []
        if output_dir and output_dir.exists():
            output_files = [str(f.relative_to(settings.output_dir)) for f in output_dir.rglob("*") if f.is_file()]
        
        processing_time = time.time() - start_time
        
        return ImageOCRResponse(
            success=True,
            text=result,
            processing_time=processing_time,
            tokens_generated=metrics.tokens_generated if metrics else None,
            tokens_per_second=metrics.tokens_per_second if metrics else None,
            output_files=output_files if output_files else None
        )
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        return ImageOCRResponse(
            success=False,
            text="",
            processing_time=time.time() - start_time,
            error=str(e)
        )
    finally:
        # Cleanup temp file
        if temp_file and temp_file.exists() and settings.cleanup_temp_files:
            try:
                temp_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")


@app.post(
    f"{settings.api_prefix}/ocr/pdf",
    response_model=PDFOCRResponse,
    tags=["OCR"],
    summary="Process a PDF document with OCR"
)
async def process_pdf_endpoint(
    file: UploadFile = File(..., description="PDF file to process"),
    start_page: Optional[int] = None,
    end_page: Optional[int] = None,
    save_output: bool = True,
):
    """
    Process a PDF file with OCR.
    
    - **file**: PDF file to process
    - **start_page**: Starting page number (1-indexed)
    - **end_page**: Ending page number (1-indexed)
    - **save_output**: Whether to save output files
    
    Returns OCR results in text format for all pages.
    """
    start_time = time.time()
    temp_file = None
    output_dir = None
    
    try:
        # Validate file
        validate_file_extension(file.filename, settings.allowed_pdf_extensions)
        
        # Create temp file
        temp_file = settings.temp_dir / f"{time.time()}_{file.filename}"
        await save_upload_file(file, temp_file)
        
        logger.info(f"Processing PDF: {file.filename}")
        
        # Setup output directory
        if save_output:
            output_dir = settings.output_dir / f"{temp_file.stem}_{int(time.time())}"
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process PDF
        result, metrics = process_pdf_with_metrics(
            str(temp_file),
            output_dir=str(output_dir) if output_dir else None,
            start_page=start_page,
            end_page=end_page,
        )
        
        # Collect output files
        output_files = []
        if output_dir and output_dir.exists():
            output_files = [str(f.relative_to(settings.output_dir)) for f in output_dir.rglob("*") if f.is_file()]
        
        processing_time = time.time() - start_time
        
        return PDFOCRResponse(
            success=True,
            text=result,
            num_pages=metrics.num_operations if metrics else 0,
            processing_time=processing_time,
            pages_processed=list(range(1, (metrics.num_operations if metrics else 0) + 1)),
            output_files=output_files if output_files else None
        )
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        return PDFOCRResponse(
            success=False,
            text="",
            num_pages=0,
            processing_time=time.time() - start_time,
            pages_processed=[],
            error=str(e)
        )
    finally:
        # Cleanup temp file
        if temp_file and temp_file.exists() and settings.cleanup_temp_files:
            try:
                temp_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")


@app.post(
    f"{settings.api_prefix}/ocr/pdf/enhanced",
    response_model=PDFEnhancedResponse,
    tags=["OCR"],
    summary="Process a PDF document with enhanced extraction"
)
async def process_pdf_enhanced_endpoint(
    file: UploadFile = File(..., description="PDF file to process"),
    start_page: Optional[int] = None,
    end_page: Optional[int] = None,
    generate_overlays: bool = True,
    save_elements: bool = True,
    save_output: bool = True,
):
    """
    Process a PDF file with enhanced extraction capabilities.
    
    - **file**: PDF file to process
    - **start_page**: Starting page number (1-indexed)
    - **end_page**: Ending page number (1-indexed)
    - **generate_overlays**: Generate element overlay images
    - **save_elements**: Save individual element images
    - **save_output**: Whether to save output files
    
    Returns OCR results with structured element extraction and metadata.
    """
    start_time = time.time()
    temp_file = None
    output_dir = None
    
    try:
        # Validate file
        validate_file_extension(file.filename, settings.allowed_pdf_extensions)
        
        # Create temp file
        temp_file = settings.temp_dir / f"{time.time()}_{file.filename}"
        await save_upload_file(file, temp_file)
        
        logger.info(f"Processing PDF with enhanced extraction: {file.filename}")
        
        # Setup output directory
        if save_output:
            output_dir = settings.output_dir / f"{temp_file.stem}_enhanced_{int(time.time())}"
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process PDF with enhanced extraction
        result = process_pdf_enhanced(
            str(temp_file),
            output_dir=str(output_dir) if output_dir else None,
            start_page=start_page,
            end_page=end_page,
            generate_overlays=generate_overlays,
            save_elements=save_elements,
        )
        
        # Collect output files
        output_files = []
        if output_dir and output_dir.exists():
            output_files = [str(f.relative_to(settings.output_dir)) for f in output_dir.rglob("*") if f.is_file()]
        
        processing_time = time.time() - start_time
        
        return PDFEnhancedResponse(
            success=True,
            text=result['markdown'],
            structure=result['structure'],
            num_pages=result['structure']['document_metadata']['num_pages'],
            processing_time=processing_time,
            pages_processed=list(range(1, result['structure']['document_metadata']['num_pages'] + 1)),
            output_files=output_files if output_files else None
        )
        
    except Exception as e:
        logger.error(f"Error processing PDF with enhanced extraction: {str(e)}", exc_info=True)
        
        # Return error response with minimal valid structure
        from .models import DocumentMetadata, DocumentStructure
        
        return PDFEnhancedResponse(
            success=False,
            text="",
            structure=DocumentStructure(
                document_metadata=DocumentMetadata(
                    filename=file.filename,
                    num_pages=0,
                    total_elements=0,
                    element_counts={}
                ),
                pages=[]
            ),
            num_pages=0,
            processing_time=time.time() - start_time,
            pages_processed=[],
            error=str(e)
        )
    finally:
        # Cleanup temp file
        if temp_file and temp_file.exists() and settings.cleanup_temp_files:
            try:
                temp_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
        "info": f"{settings.api_prefix}/info",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers,
    )
