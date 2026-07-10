"""
Document Type Schemas
Land Intelligence System
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DocumentTypeCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    requires_verification: bool = False
    retention_years: str = "PERMANENT"


class DocumentTypeUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    requires_verification: Optional[bool] = None
    retention_years: Optional[str] = None


class DocumentTypeResponse(BaseModel):
    """Schema for returning DocumentType data to API client."""
    id: str = Field(..., description="UUID primary key")
    name: str = Field(..., description="Document type name")
    code: str = Field(..., description="Document type code")
    description: Optional[str] = Field(None, description="Description of document type")
    requires_verification: bool = Field(..., description="Whether documents require verification")
    retention_years: str = Field(..., description="Retention period")
    is_active: bool = Field(..., description="Soft delete flag")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    updated_at: datetime = Field(..., description="Timestamp when record was last updated")
    
    model_config = ConfigDict(from_attributes=True)


class DocumentTypeListResponse(BaseModel):
    """Schema for paginated document type list response."""
    items: list[DocumentTypeResponse]
    total: int
    page: int
    size: int
    pages: int