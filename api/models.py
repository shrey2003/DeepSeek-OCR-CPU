"""Pydantic models for API request/response."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str


class ModelInfo(BaseModel):
    """Model information response."""
    model_name: str
    device: str
    version: str


class ImageOCRRequest(BaseModel):
    """Request model for image OCR."""
    return_bbox: bool = Field(default=False, description="Return bounding box data")
    save_output: bool = Field(default=True, description="Save output files")


class ImageOCRResponse(BaseModel):
    """Response model for image OCR."""
    success: bool
    text: str
    processing_time: float
    tokens_generated: Optional[int] = None
    tokens_per_second: Optional[float] = None
    output_files: Optional[List[str]] = None
    bbox_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PDFOCRRequest(BaseModel):
    """Request model for PDF OCR."""
    max_pages: Optional[int] = Field(default=None, description="Maximum pages to process")
    start_page: Optional[int] = Field(default=None, description="Starting page (1-indexed)")
    end_page: Optional[int] = Field(default=None, description="Ending page (1-indexed)")
    save_output: bool = Field(default=True, description="Save output files")


class PDFOCRResponse(BaseModel):
    """Response model for PDF OCR."""
    success: bool
    text: str
    num_pages: int
    processing_time: float
    pages_processed: List[int]
    output_files: Optional[List[str]] = None
    error: Optional[str] = None


class PDFEnhancedRequest(BaseModel):
    """Request model for enhanced PDF OCR."""
    max_pages: Optional[int] = Field(default=None, description="Maximum pages to process")
    start_page: Optional[int] = Field(default=None, description="Starting page (1-indexed)")
    end_page: Optional[int] = Field(default=None, description="Ending page (1-indexed)")
    generate_overlays: bool = Field(default=True, description="Generate element overlay images")
    save_elements: bool = Field(default=True, description="Save individual element images")
    save_output: bool = Field(default=True, description="Save output files")


class ElementMetadata(BaseModel):
    """Metadata for an extracted element."""
    type: str
    bbox: List[float]
    confidence: Optional[float] = None
    content: Optional[str] = None


class PageStructure(BaseModel):
    """Structure information for a page."""
    page_number: int
    elements: List[ElementMetadata]
    element_counts: Dict[str, int]


class DocumentMetadata(BaseModel):
    """Metadata for the processed document."""
    filename: str
    num_pages: int
    total_elements: int
    element_counts: Dict[str, int]


class DocumentStructure(BaseModel):
    """Complete document structure."""
    document_metadata: DocumentMetadata
    pages: List[PageStructure]


class PDFEnhancedResponse(BaseModel):
    """Response model for enhanced PDF OCR."""
    success: bool
    text: str
    structure: DocumentStructure
    num_pages: int
    processing_time: float
    pages_processed: List[int]
    output_files: Optional[List[str]] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
