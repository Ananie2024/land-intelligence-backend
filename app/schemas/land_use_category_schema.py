"""
Land Use Category Schemas
Land Intelligence System
"""

from typing import Optional
from pydantic import BaseModel


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