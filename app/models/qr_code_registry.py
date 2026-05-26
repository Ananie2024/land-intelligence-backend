# app/models/qr_code_registry.py
"""
QR Code Registry Model
Phase 2 — Section 3.1
Land Intelligence System
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, JSON, Integer
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from app.models.base import BaseModel


class QRCodeRegistry(BaseModel):
    """
    QR code registry entity representing QR codes generated per parcel/document.
    
    Attributes:
        id: UUID primary key (inherited from BaseModel)
        parcel_id: Foreign key to parcel (optional)
        document_id: Foreign key to document (optional)
        code: Unique QR code string
        code_type: Type of entity this QR code points to (parcel, document)
        file_path: Path to QR code image file
        data_payload: JSON data encoded in QR code
        expires_at: Expiration timestamp (if temporary)
        last_accessed_at: Last time this QR was scanned
        access_count: Number of times QR has been accessed
        is_revoked: Whether this QR code has been revoked
        metadata: JSON field for additional attributes
        is_active: Soft delete flag (inherited from BaseModel)
        created_at: Timestamp when record was created (inherited)
        updated_at: Timestamp when record was last updated (inherited)
    """
    
    __tablename__ = "qr_code_registry"
    
    parcel_id = Column(
        CHAR(36),
        ForeignKey("parcels.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Foreign key to parcel (optional)"
    )
    
    document_id = Column(
        CHAR(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Foreign key to document (optional)"
    )
    
    code = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique QR code string"
    )
    
    code_type = Column(
        String(20),
        nullable=False,
        index=True,
        comment="Type of entity this QR code points to (parcel, document)"
    )
    
    file_path = Column(
        String(500),
        nullable=False,
        comment="Path to QR code image file"
    )
    
    data_payload = Column(
        JSON,
        nullable=False,
        comment="JSON data encoded in QR code"
    )
    
    expires_at = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="Expiration timestamp (if temporary)"
    )
    
    last_accessed_at = Column(
        DateTime,
        nullable=True,
        comment="Last time this QR was scanned"
    )
    
    access_count = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Number of times QR has been accessed"
    )
    
    is_revoked = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        comment="Whether this QR code has been revoked"
    )
    
    extra_data = Column(
        "metadata",
        JSON,
        nullable=True,
        comment="JSON field for additional attributes"
    )
    
    # Relationships
    parcel = relationship(
        "Parcel",
        back_populates="qr_codes"
    )
    
    document = relationship(
        "Document",
        back_populates="qr_codes"
    )
    
    # Indexes for search
    __table_args__ = (
        Index('idx_code_type', 'code_type'),
        Index('idx_expires_at', 'expires_at'),
        Index('idx_is_revoked', 'is_revoked'),
        # Ensure at least one reference exists
    )
    
    def __repr__(self):
        """String representation of QRCodeRegistry instance."""
        return f"<QRCodeRegistry(code='{self.code[:20]}...', type='{self.code_type}')>"