# app/models/land_use_category.py
"""
Land Use Category Model
Phase 2 — Section 3.1
Land Intelligence System
"""

from sqlalchemy import Column, String, Text, Float, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class LandUseCategory(BaseModel):
    """
    Land use category entity representing classifications of land use.
    
    Attributes:
        id: UUID primary key (inherited from BaseModel)
        name: Category name (e.g., "Residential", "Agricultural")
        code: Unique category code (e.g., "RES", "AGR")
        description: Description of land use category
        base_tax_rate: Base tax rate per square meter
        tax_rate_unit: Unit for tax rate (e.g., "per_sqm", "flat")
        requires_approval: Whether this land use requires special approval
        zoning_restrictions: Any zoning restrictions applicable
        is_active: Soft delete flag (inherited from BaseModel)
        created_at: Timestamp when record was created (inherited)
        updated_at: Timestamp when record was last updated (inherited)
    """
    
    __tablename__ = "land_use_categories"
    
    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Category name (e.g., 'Residential', 'Agricultural')"
    )
    
    code = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique category code (e.g., 'RES', 'AGR')"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Description of land use category"
    )
    
    base_tax_rate = Column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0",
        comment="Base tax rate per square meter"
    )
    
    tax_rate_unit = Column(
        String(20),
        nullable=False,
        default="per_sqm",
        server_default="per_sqm",
        comment="Unit for tax rate (e.g., 'per_sqm', 'flat')"
    )
    
    requires_approval = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        comment="Whether this land use requires special approval"
    )
    
    zoning_restrictions = Column(
        Text,
        nullable=True,
        comment="Any zoning restrictions applicable"
    )
    
    # Relationships
    parcels = relationship(
        "Parcel",
        back_populates="land_use_category"
    )
    
    def __repr__(self):
        """String representation of LandUseCategory instance."""
        return f"<LandUseCategory(name='{self.name}', code='{self.code}', rate={self.base_tax_rate})>"