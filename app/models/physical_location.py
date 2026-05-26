"""
Physical Location Model
Phase 2 — Section 3.1
Land Intelligence System
"""

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from app.models.base import BaseModel


class PhysicalLocation(BaseModel):
    """
    Physical location entity representing archive rooms and buildings.
    
    Attributes:
        id: UUID primary key (inherited from BaseModel)
        document_id: Foreign key to document (optional, for direct document location)
        name: Location name (e.g., "Main Archive Room", "Basement Storage")
        location_code: Unique location code (e.g., "ARC-01", "BSM-02")
        building: Building name or number
        floor: Floor level
        room_number: Room number or identifier
        description: Description of location and access instructions
        environmental_notes: Notes about environmental conditions (humidity, temperature)
        access_restrictions: Any access restrictions or security requirements
        contact_person: Person responsible for this location
        contact_phone: Contact phone number
        is_active: Soft delete flag (inherited from BaseModel)
        created_at: Timestamp when record was created (inherited)
        updated_at: Timestamp when record was last updated (inherited)
    """
    
    __tablename__ = "physical_locations"
    
    document_id = Column(
        CHAR(36),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
        comment="Foreign key to document (optional, for direct document location)"
    )
    
    name = Column(
        String(200),
        nullable=False,
        comment="Location name (e.g., 'Main Archive Room', 'Basement Storage')"
    )
    
    location_code = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique location code (e.g., 'ARC-01', 'BSM-02')"
    )
    
    building = Column(
        String(100),
        nullable=True,
        comment="Building name or number"
    )
    
    floor = Column(
        String(50),
        nullable=True,
        comment="Floor level"
    )
    
    room_number = Column(
        String(50),
        nullable=True,
        comment="Room number or identifier"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Description of location and access instructions"
    )
    
    environmental_notes = Column(
        Text,
        nullable=True,
        comment="Notes about environmental conditions (humidity, temperature)"
    )
    
    access_restrictions = Column(
        Text,
        nullable=True,
        comment="Any access restrictions or security requirements"
    )
    
    contact_person = Column(
        String(200),
        nullable=True,
        comment="Person responsible for this location"
    )
    
    contact_phone = Column(
        String(50),
        nullable=True,
        comment="Contact phone number"
    )
    
    # Relationships
    document = relationship(
        "Document",
        back_populates="physical_location"
    )
    
    storage_cabinets = relationship(
        "StorageCabinet",
        back_populates="physical_location",
        cascade="all, delete-orphan"
    )
    
    # Indexes for search
    __table_args__ = (
        Index('idx_location_code', 'location_code'),
        Index('idx_building_floor', 'building', 'floor'),
    )
    
    def __repr__(self):
        """String representation of PhysicalLocation instance."""
        return f"<PhysicalLocation(name='{self.name}', code='{self.location_code}')>"# app/models/physical_location.py
