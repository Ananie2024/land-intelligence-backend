# app/models/parcel.py
"""
Parcel Model
Phase 2 — Section 3.1
Land Intelligence System
"""

from sqlalchemy import Column, String, Text, Float, ForeignKey, Integer, Boolean, JSON
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from app.models.base import BaseModel


class Parcel(BaseModel):
    """
    Land parcel entity representing a plot of land.
    
    Attributes:
        id: UUID primary key (inherited from BaseModel)
        parcel_number: Unique parcel identifier
        parish_id: Foreign key to parish
        land_use_category_id: Foreign key to land use category
        area_sqm: Area in square meters
        geometry_wkb: Spatial geometry in WKB format (handled by application)
        title_deed_number: Official title deed reference
        owner_name: Name of land owner
        owner_contact: Contact information for owner
        location_description: Text description of location
        valuation: Current valuation amount
        valuation_date: Date of last valuation
        metadata: JSON field for additional attributes
        is_active: Soft delete flag (inherited from BaseModel)
        created_at: Timestamp when record was created (inherited)
        updated_at: Timestamp when record was last updated (inherited)
    """
    
    __tablename__ = "parcels"
    
    parcel_number = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique parcel identifier"
    )
    
    parish_id = Column(
        CHAR(36),
        ForeignKey("parishes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Foreign key to parish"
    )
    
    land_use_category_id = Column(
        CHAR(36),
        ForeignKey("land_use_categories.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="Foreign key to land use category"
    )
    
    area_sqm = Column(
        Float,
        nullable=False,
        comment="Area in square meters"
    )
    
    geometry_wkb = Column(
        String(10000),  # WKB hex string storage
        nullable=True,
        comment="Spatial geometry in WKB format (hex)"
    )
    
    title_deed_number = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Official title deed reference"
    )
    
    owner_name = Column(
        String(500),
        nullable=False,
        comment="Name of land owner"
    )
    
    owner_contact = Column(
        String(500),
        nullable=True,
        comment="Contact information for owner"
    )
    
    location_description = Column(
        Text,
        nullable=True,
        comment="Text description of location"
    )
    
    valuation = Column(
        Float,
        nullable=True,
        comment="Current valuation amount"
    )
    
    valuation_date = Column(
        String(10),  # ISO date YYYY-MM-DD
        nullable=True,
        comment="Date of last valuation"
    )
    
    extra_data = Column(
        "metadata",
        JSON,
        nullable=True,
        comment="JSON field for additional attributes"
    )
    
    # Relationships
    parish = relationship(
        "Parish",
        back_populates="parcels"
    )
    
    land_use_category = relationship(
        "LandUseCategory",
        back_populates="parcels"
    )
    
    documents = relationship(
        "Document",
        back_populates="parcel",
        cascade="all, delete-orphan"
    )
    
    tax_records = relationship(
        "TaxRecord",
        back_populates="parcel",
        cascade="all, delete-orphan"
    )
    
    qr_codes = relationship(
        "QRCodeRegistry",
        back_populates="parcel",
        cascade="all, delete-orphan"
    )
    
    # Indexes for spatial and text search
    __table_args__ = (
        Index('idx_parcel_number', 'parcel_number'),
        Index('idx_owner_name', 'owner_name'),
        Index('idx_title_deed', 'title_deed_number'),
        # Note: Spatial indexes will be added in migration
    )
    
    def __repr__(self):
        """String representation of Parcel instance."""
        return f"<Parcel(parcel_number='{self.parcel_number}', owner='{self.owner_name[:30]}...')>"