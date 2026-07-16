# app/models/parish.py
"""
Parish Model
Phase 2 — Section 3.1
Land Intelligence System
"""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from app.models.base import BaseModel


class Parish(BaseModel):
    """
    Parish entity representing administrative land divisions.
    
    Simplified to only include parish name - other data is kept in other systems.
    
    Attributes:
        id: UUID primary key (inherited from BaseModel)
        name: Official parish name
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
        return f"<Parish(name='{self.name}')>"