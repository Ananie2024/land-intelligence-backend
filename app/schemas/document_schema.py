# app/schemas/document_schema.py
"""
Document Schemas
Phase 2 — Section 3.2
Land Intelligence System
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime, date


class DocumentBase(BaseModel):
    """
    Base schema for Document with shared fields.
    Used as base for both Create and Response schemas.
    """
    parcel_id: Optional[str] = Field(None, description="Foreign key to parcel (optional)")
    document_type_id: str = Field(..., description="Foreign key to document type")
    filename: str = Field(..., max_length=500, description="Original filename")
    description: Optional[str] = Field(None, description="Document description")
    document_date: Optional[date] = Field(None, description="Document date (issue/recording date)")
    reference_number: Optional[str] = Field(None, max_length=200, description="Official reference number")
    page_count: Optional[int] = Field(None, ge=0, description="Number of pages (for PDF)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="JSON field for additional attributes")


class DocumentCreate(DocumentBase):
    """
    Schema for creating a new Document.
    Excludes id and timestamps. File metadata is populated by the system.
    """
    file_path: Optional[str] = Field(None, max_length=500, description="Path to file on filesystem")
    file_size_bytes: Optional[int] = Field(None, ge=0, description="Size of file in bytes")
    mime_type: Optional[str] = Field(None, max_length=100, description="MIME type of file")
    checksum: Optional[str] = Field(None, max_length=64, description="SHA-256 checksum for integrity")


class DocumentUploadRequest(BaseModel):
    """
    Schema for document upload request with metadata.
    File upload is handled separately as form data.
    """
    parcel_id: Optional[str] = Field(None, description="Foreign key to parcel")
    document_type_id: str = Field(..., description="Foreign key to document type")
    description: Optional[str] = Field(None, description="Document description")
    document_date: Optional[date] = Field(None, description="Document date")
    reference_number: Optional[str] = Field(None, max_length=200, description="Official reference number")


class DocumentUpdate(BaseModel):
    """
    Schema for updating an existing Document.
    All fields are optional for partial updates.
    """
    parcel_id: Optional[str] = Field(None, description="Foreign key to parcel")
    document_type_id: Optional[str] = Field(None, description="Foreign key to document type")
    filename: Optional[str] = Field(None, max_length=500, description="Original filename")
    description: Optional[str] = Field(None, description="Document description")
    document_date: Optional[date] = Field(None, description="Document date")
    reference_number: Optional[str] = Field(None, max_length=200, description="Official reference number")
    page_count: Optional[int] = Field(None, ge=0, description="Number of pages")
    metadata: Optional[Dict[str, Any]] = Field(None, description="JSON field for additional attributes")
    is_active: Optional[bool] = Field(None, description="Soft delete flag")


class DocumentResponse(DocumentBase):
    """
    Schema for returning Document data to API client.
    Includes id, timestamps, and file metadata.
    """
    id: str = Field(..., description="UUID primary key")
    file_path: str = Field(..., description="Path to file on filesystem")
    file_size_bytes: int = Field(..., ge=0, description="Size of file in bytes")
    mime_type: str = Field(..., description="MIME type of file")
    checksum: str = Field(..., max_length=64, description="SHA-256 checksum for integrity")
    is_active: bool = Field(..., description="Soft delete flag")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    updated_at: datetime = Field(..., description="Timestamp when record was last updated")
    
    # Optional nested relationship data
    document_type_name: Optional[str] = Field(None, description="Document type name (when included)")
    parcel_number: Optional[str] = Field(None, description="Parcel number (when included)")
    qr_code_count: int = Field(0, description="Number of associated QR codes")
    
    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """
    Schema for paginated document list response.
    """
    items: list[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int


class DocumentSearchParams(BaseModel):
    """
    Schema for document search/filter parameters.
    """
    parcel_id: Optional[str] = Field(None, description="Filter by parcel")
    document_type_id: Optional[str] = Field(None, description="Filter by document type")
    filename: Optional[str] = Field(None, max_length=500, description="Filter by filename (partial match)")
    reference_number: Optional[str] = Field(None, max_length=200, description="Filter by reference number")
    from_date: Optional[date] = Field(None, description="Filter documents from this date")
    to_date: Optional[date] = Field(None, description="Filter documents up to this date")
    is_active: Optional[bool] = Field(True, description="Filter by active status")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Items per page")
