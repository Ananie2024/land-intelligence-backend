# app/models/storage_cabinet.py
"""
Storage Cabinet Model
Phase 2 — Section 3.1
Land Intelligence System
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from app.models.base import BaseModel


class StorageCabinet(BaseModel):
    """
    Storage cabinet entity representing physical storage locations for paper documents.
    
    Attributes:
        id: UUID primary key (inherited from BaseModel)
        physical_location_id: Foreign key to physical location (room/building)
        cabinet_number: Cabinet identifier (e.g., "CAB-001")
        cabinet_type: Type of cabinet (e.g., "filing", "shelf", "drawer")
        description: Description of cabinet contents/location
        row_number: Row number within location (if applicable)
        column_number: Column number within location (if applicable)
        max_capacity: Maximum document capacity
        current_count: Current number of documents stored
        metadata: JSON field for additional attributes
        is_active: Soft delete flag (inherited from BaseModel)
        created_at: Timestamp when record was created (inherited)
        updated_at: Timestamp when record was last updated (inherited)
    """
    
    __tablename__ = "storage_cabinets"
    
    physical_location_id = Column(UUID(as_uuid=True),
        ForeignKey("physical_locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to physical location (room/building)"
    )
    
    cabinet_number = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Cabinet identifier (e.g., 'CAB-001')"
    )
    
    cabinet_type = Column(
        String(50),
        nullable=False,
        default="filing",
        server_default="filing",
        comment="Type of cabinet (e.g., 'filing', 'shelf', 'drawer')"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Description of cabinet contents/location"
    )
    
    row_number = Column(
        Integer,
        nullable=True,
        comment="Row number within location (if applicable)"
    )
    
    column_number = Column(
        Integer,
        nullable=True,
        comment="Column number within location (if applicable)"
    )
    
    max_capacity = Column(
        Integer,
        nullable=True,
        comment="Maximum document capacity"
    )
    
    current_count = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Current number of documents stored"
    )
    
    # Relationships
    physical_location = relationship(
        "PhysicalLocation",
        back_populates="storage_cabinets"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_cabinet_number', 'cabinet_number'),
        Index('idx_cabinet_type', 'cabinet_type'),
        # Ensure cabinet numbers are unique within a physical location
        Index('idx_unique_cabinet_per_location', 'physical_location_id', 'cabinet_number', unique=True),
    )
    
    def __repr__(self):
        """String representation of StorageCabinet instance."""
        return f"<StorageCabinet(cabinet_number='{self.cabinet_number}', type='{self.cabinet_type}')>"