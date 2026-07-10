"""
Land Use Category Schemas
Land Intelligence System
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class LandUseCategoryCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    base_tax_rate: float = 0.0
    tax_rate_unit: str = "per_sqm"
    requires_approval: bool = False
    zoning_restrictions: Optional[str] = None


class LandUseCategoryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    base_tax_rate: Optional[float] = None
    tax_rate_unit: Optional[str] = None
    requires_approval: Optional[bool] = None
    zoning_restrictions: Optional[str] = None


class LandUseCategoryResponse(BaseModel):
    """Schema for returning LandUseCategory data to API client."""
    id: str = Field(..., description="UUID primary key")
    name: str = Field(..., description="Category name")
    code: str = Field(..., description="Category code")
    description: Optional[str] = Field(None, description="Description of land use category")
    base_tax_rate: float = Field(..., description="Base tax rate per square meter")
    tax_rate_unit: str = Field(..., description="Unit for tax rate")
    requires_approval: bool = Field(..., description="Whether this land use requires special approval")
    zoning_restrictions: Optional[str] = Field(None, description="Any zoning restrictions applicable")
    is_active: bool = Field(..., description="Soft delete flag")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    updated_at: datetime = Field(..., description="Timestamp when record was last updated")
    
    model_config = ConfigDict(from_attributes=True)


class LandUseCategoryListResponse(BaseModel):
    """Schema for paginated land use category list response."""
    items: list[LandUseCategoryResponse]
    total: int
    page: int
    size: int
    pages: int