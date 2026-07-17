"""
Document Type Schemas
Land Intelligence System
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.enums import DocumentType


class DocumentTypeCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    requires_verification: bool = False
    retention_years: str = "PERMANENT"

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate that code is a valid DocumentType enum value."""
        valid_codes = [dt.value for dt in DocumentType]
        if v not in valid_codes:
            raise ValueError(f"Invalid document type code. Must be one of: {', '.join(valid_codes)}")
        return v


class DocumentTypeUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    requires_verification: Optional[bool] = None
    retention_years: Optional[str] = None

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate that code is a valid DocumentType enum value if provided."""
        if v is not None:
            valid_codes = [dt.value for dt in DocumentType]
            if v not in valid_codes:
                raise ValueError(f"Invalid document type code. Must be one of: {', '.join(valid_codes)}")
        return v


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