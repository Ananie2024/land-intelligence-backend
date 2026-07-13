# app/models/parcel.py
"""
Parcel Model
Phase 2 — Section 3.1
Land Intelligence System
"""

from sqlalchemy import Column, String, Text, Float, ForeignKey, JSON, Date
from sqlalchemy import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Index
from geoalchemy2 import Geometry

from app.models.base import BaseModel


class Parcel(BaseModel):
    """
    Land parcel entity representing a plot of land.
    
    Attributes:
        id: UUID primary key (inherited from BaseModel)
        upi: Unique Parcel Identifier (UPI) — e.g. 1/02/02/03/1390
        parish_id: Foreign key to parish
        land_use_category_id: Foreign key to land use category
        area_sqm: Area in square meters
        geometry: Spatial geometry (POLYGON) in WGS84 (SRID 4326)
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
    
    upi = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique Parcel Identifier (UPI) — e.g. 1/02/02/03/1390"
    )
    
    parish_id = Column(UUID(as_uuid=True),
        ForeignKey("parishes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Foreign key to parish"
    )
    
    land_use_category_id = Column(UUID(as_uuid=True),
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
        Geometry(geometry_type='POLYGON', srid=4326),
        nullable=True,
        comment="Spatial geometry (POLYGON) in WGS84"
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
        Date,
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
    
    ownership_history = relationship(
        "ParcelOwnershipHistory",
        back_populates="parcel",
        cascade="all, delete-orphan",
        order_by="desc(ParcelOwnershipHistory.transfer_date)"
    )
    
    # Indexes for spatial and text search
    __table_args__ = (
        Index('idx_parcel_upi', 'upi'),
        Index('idx_owner_name', 'owner_name'),
        Index('idx_title_deed', 'title_deed_number'),
        # Note: Spatial index for 'geometry' column
    )
    
    def __repr__(self):
        """String representation of Parcel instance."""
        return f"<Parcel(upi='{self.upi}', owner='{self.owner_name[:30]}...')>"
