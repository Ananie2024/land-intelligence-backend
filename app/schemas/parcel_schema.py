# app/schemas/parcel_schema.py
"""
Parcel Schemas
Phase 2 — Section 3.2
Land Intelligence System
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Any, Dict
from datetime import datetime, date
import binascii


class ParcelBase(BaseModel):
    """
    Base schema for Parcel with shared fields.
    Used as base for both Create and Response schemas.
    """
    upi: str = Field(..., max_length=50, description="Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390")
    parish_id: str = Field(..., description="Foreign key to parish")
    land_use_category_id: Optional[str] = Field(None, description="Foreign key to land use category")
    area_sqm: float = Field(..., gt=0, description="Area in square meters")
    geometry_wkb: Optional[str] = Field(None, description="Spatial geometry in WKB format (hex)")
    title_deed_number: Optional[str] = Field(None, max_length=100, description="Official title deed reference")
    owner_name: str = Field(..., max_length=500, description="Name of land owner")
    owner_contact: Optional[str] = Field(None, max_length=500, description="Contact information for owner")
    location_description: Optional[str] = Field(None, description="Text description of location")
    valuation: Optional[float] = Field(None, ge=0, description="Current valuation amount")
    valuation_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date of last valuation (YYYY-MM-DD)")
    extra_data: Optional[Dict[str, Any]] = Field(
        None,
        alias="metadata",
        description="JSON field for additional attributes",
    )

    @field_validator("geometry_wkb", mode="before")
    @classmethod
    def validate_geometry(cls, v: Any) -> Optional[str]:
        """Convert GeoAlchemy2 WKBElement to hex string."""
        if v is None:
            return None
        if hasattr(v, "data"):
            if isinstance(v.data, bytes):
                return binascii.hexlify(v.data).decode("ascii").upper()
            return str(v.data)
        return v

    model_config = ConfigDict(populate_by_name=True)


class ParcelCreate(ParcelBase):
    """Schema for creating a new Parcel."""
    pass


class ParcelUpdate(BaseModel):
    """Schema for updating an existing Parcel. All fields are optional for partial updates."""
    upi: Optional[str] = Field(None, max_length=50, description="Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390")
    parish_id: Optional[str] = Field(None, description="Foreign key to parish")
    land_use_category_id: Optional[str] = Field(None, description="Foreign key to land use category")
    area_sqm: Optional[float] = Field(None, gt=0, description="Area in square meters")
    geometry_wkb: Optional[str] = Field(None, description="Spatial geometry in WKB format (hex)")
    title_deed_number: Optional[str] = Field(None, max_length=100, description="Official title deed reference")
    owner_name: Optional[str] = Field(None, max_length=500, description="Name of land owner")
    owner_contact: Optional[str] = Field(None, max_length=500, description="Contact information for owner")
    location_description: Optional[str] = Field(None, description="Text description of location")
    valuation: Optional[float] = Field(None, ge=0, description="Current valuation amount")
    valuation_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date of last valuation")
    extra_data: Optional[Dict[str, Any]] = Field(
        None,
        alias="metadata",
        description="JSON field for additional attributes",
    )
    is_active: Optional[bool] = Field(None, description="Soft delete flag")

    model_config = ConfigDict(populate_by_name=True)


class ParcelResponse(ParcelBase):
    """Schema for returning Parcel data to API client."""
    id: str = Field(..., description="UUID primary key")
    is_active: bool = Field(..., description="Soft delete flag")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    updated_at: datetime = Field(..., description="Timestamp when record was last updated")
    parish_name: Optional[str] = Field(None, description="Parish name (when included)")
    land_use_category_name: Optional[str] = Field(None, description="Land use category name (when included)")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ParcelListResponse(BaseModel):
    """Schema for paginated parcel list response."""
    items: list[ParcelResponse]
    total: int
    page: int
    size: int
    pages: int


class ParcelSearchParams(BaseModel):
    """Schema for parcel search/filter parameters."""
    parish_id: Optional[str] = Field(None, description="Filter by parish")
    land_use_category_id: Optional[str] = Field(None, description="Filter by land use category")
    owner_name: Optional[str] = Field(None, max_length=500, description="Filter by owner name (partial match)")
    upi: Optional[str] = Field(None, max_length=50, description="Filter by UPI (partial match)")
    title_deed_number: Optional[str] = Field(None, max_length=100, description="Filter by title deed number")
    min_area_sqm: Optional[float] = Field(None, ge=0, description="Minimum area in square meters")
    max_area_sqm: Optional[float] = Field(None, ge=0, description="Maximum area in square meters")
    is_active: Optional[bool] = Field(True, description="Filter by active status")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Items per page")


class ParcelOwnershipHistoryResponse(BaseModel):
    """Schema for ownership history entry."""
    id: str = Field(..., description="UUID primary key")
    parcel_upi: str = Field(..., description="Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390")
    owner_name: str = Field(..., description="Owner name at time of record")
    owner_contact: Optional[str] = Field(None, description="Owner contact information")
    transfer_date: date = Field(..., description="Date of ownership transfer")
    document_reference: Optional[str] = Field(None, description="Supporting document reference")
    notes: Optional[str] = Field(None, description="Additional notes")
    is_active: bool = Field(..., description="Soft delete flag")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    updated_at: datetime = Field(..., description="Timestamp when record was last updated")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)