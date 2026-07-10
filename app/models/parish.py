# app/models/parish.py
"""
Parish Model
Phase 2 — Section 3.1
Land Intelligence System
"""

from sqlalchemy import Column, String, Text, Integer, func
from sqlalchemy.orm import relationship
from sqlalchemy import Index
from geoalchemy2 import Geometry

from app.models.base import BaseModel


class Parish(BaseModel):
    """
    Parish entity representing administrative land divisions.
    
    Attributes:
        id: UUID primary key (inherited from BaseModel)
        name: Official parish name
        code: Unique parish code (e.g., "PAR-001")
        description: Description of parish boundaries and history
        address: Physical address of parish office
        contact_person: Name of primary contact person
        contact_phone: Phone number for parish office
        contact_email: Email address for parish office
        parcel_count: Cached count of active parcels in this parish
        boundary_wkb: Spatial boundary in WKB format
        is_active: Soft delete flag (inherited from BaseModel)
        created_at: Timestamp when record was created (inherited)
        updated_at: Timestamp when record was last updated (inherited)
    """
    
    __tablename__ = "parishes"
    
    name = Column(
        String(200),
        nullable=False,
        comment="Official parish name"
    )
    
    code = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique parish code (e.g., 'PAR-001')"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Description of parish boundaries and history"
    )
    
    address = Column(
        String(500),
        nullable=True,
        comment="Physical address of parish office"
    )
    
    contact_person = Column(
        String(200),
        nullable=True,
        comment="Name of primary contact person"
    )
    
    contact_phone = Column(
        String(50),
        nullable=True,
        comment="Phone number for parish office"
    )
    
    contact_email = Column(
        String(200),
        nullable=True,
        comment="Email address for parish office"
    )
    
    parcel_count = Column(
        Integer,
        nullable=False,
        server_default="0",
        comment="Cached count of active parcels in this parish"
    )
    
    boundary_wkb = Column(
        Geometry(geometry_type='MULTIPOLYGON', srid=4326),
        nullable=True,
        comment="Spatial boundary of the parish (MULTIPOLYGON) in WGS84"
    )
    
    # Relationships
    parcels = relationship(
        "Parcel",
        back_populates="parish",
    )
    
    # Indexes for search
    __table_args__ = (
        Index('ix_parishes_name', 'name'),
    )
    
    def __repr__(self):
        """String representation of Parish instance."""
        return f"<Parish(name='{self.name}', code='{self.code}')>"