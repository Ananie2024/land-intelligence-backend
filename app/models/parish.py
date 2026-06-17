# app/models/parish.py
"""
Parish Model
Phase 2 — Section 3.1
Land Intelligence System
"""

from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.models.base import BaseModel


class Parish(BaseModel):
    """
    Parish entity representing administrative grouping of land parcels.
    
    Attributes:
        id: UUID primary key (inherited from BaseModel)
        name: Official parish name
        code: Unique parish code (e.g., PAR-001)
        description: Optional description of parish boundaries/history
        address: Physical address of parish office
        contact_person: Name of primary contact
        contact_phone: Phone number for parish office
        contact_email: Email address for parish office
        boundary_wkb: Spatial boundary of the parish (MULTIPOLYGON)
        parcel_count: Cached count of active parcels in this parish
        is_active: Soft delete flag (inherited from BaseModel)
        created_at: Timestamp when record was created (inherited)
        updated_at: Timestamp when record was last updated (inherited)
    """
    
    __tablename__ = "parishes"
    
    name = Column(
        String(200),
        nullable=False,
        index=True,
        comment="Official parish name"
    )
    
    code = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique parish code (e.g., PAR-001)"
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
    
    boundary_wkb = Column(
        Geometry(geometry_type='MULTIPOLYGON', srid=4326),
        nullable=True,
        comment="Spatial boundary of the parish (MULTIPOLYGON) in WGS84"
    )
    
    parcel_count = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Cached count of active parcels in this parish"
    )
    
    # Relationships
    parcels = relationship(
        "Parcel",
        back_populates="parish",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        """String representation of Parish instance."""
        return f"<Parish(name='{self.name}', code='{self.code}')>"