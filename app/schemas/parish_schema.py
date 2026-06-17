"""
Parish Schemas
Phase 2 — Section 3.2
Land Intelligence System
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Any
from datetime import datetime
import binascii


class ParishBase(BaseModel):
    """
    Base schema for Parish with shared fields.
    Used as base for both Create and Response schemas.
    """
    name: str = Field(..., max_length=200, description="Official parish name")
    code: str = Field(..., max_length=20, description="Unique parish code")
    description: Optional[str] = Field(None, description="Description of parish boundaries and history")
    address: Optional[str] = Field(None, max_length=500, description="Physical address of parish office")
    contact_person: Optional[str] = Field(None, max_length=200, description="Name of primary contact person")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Phone number for parish office")
    contact_email: Optional[str] = Field(None, max_length=200, description="Email address for parish office")
    boundary_wkb: Optional[str] = Field(None, description="Spatial boundary in WKB format (hex)")

    @field_validator("boundary_wkb", mode="before")
    @classmethod
    def validate_boundary(cls, v: Any) -> Optional[str]:
        """Convert GeoAlchemy2 WKBElement to hex string."""
        if v is None:
            return None
        if hasattr(v, "data"):
            if isinstance(v.data, bytes):
                return binascii.hexlify(v.data).decode("ascii").upper()
            return str(v.data)
        return v


class ParishCreate(ParishBase):
    """
    Schema for creating a new Parish.
    Excludes id, timestamps, and cached counts.
    """
    pass


class ParishUpdate(BaseModel):
    """
    Schema for updating an existing Parish.
    All fields are optional for partial updates.
    """
    name: Optional[str] = Field(None, max_length=200, description="Official parish name")
    code: Optional[str] = Field(None, max_length=20, description="Unique parish code")
    description: Optional[str] = Field(None, description="Description of parish boundaries and history")
    address: Optional[str] = Field(None, max_length=500, description="Physical address of parish office")
    contact_person: Optional[str] = Field(None, max_length=200, description="Name of primary contact person")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Phone number for parish office")
    contact_email: Optional[str] = Field(None, max_length=200, description="Email address for parish office")
    boundary_wkb: Optional[str] = Field(None, description="Spatial boundary in WKB format (hex)")
    parcel_count: Optional[int] = Field(None, ge=0, description="Cached count of active parcels")
    is_active: Optional[bool] = Field(None, description="Soft delete flag")


class ParishResponse(ParishBase):
    """
    Schema for returning Parish data to API client.
    Includes id, timestamps, and cached counts.
    """
    id: str = Field(..., description="UUID primary key")
    parcel_count: int = Field(..., ge=0, description="Cached count of active parcels")
    is_active: bool = Field(..., description="Soft delete flag")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    updated_at: datetime = Field(..., description="Timestamp when record was last updated")
    
    model_config = ConfigDict(from_attributes=True)


class ParishListResponse(BaseModel):
    """
    Schema for paginated parish list response.
    """
    items: list[ParishResponse]
    total: int
    page: int
    size: int
    pages: int
