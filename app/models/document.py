# app/models/document.py
"""
Document Model
Phase 2 — Section 3.1
Land Intelligence System
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Date
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from app.models.base import BaseModel


class Document(BaseModel):
    """
    Document entity representing scanned documents and files.
    
    Attributes:
        id: UUID primary key (inherited from BaseModel)
        parcel_id: Foreign key to parcel (optional)
        document_type_id: Foreign key to document type
        filename: Original filename
        file_path: Path to file on filesystem
        file_size_bytes: Size of file in bytes
        mime_type: MIME type of file
        description: Document description
        document_date: Document date (issue/recording date)
        reference_number: Official reference number
        page_count: Number of pages (for PDF)
        checksum: SHA-256 checksum for integrity
        metadata: JSON field for additional attributes
        is_active: Soft delete flag (inherited from BaseModel)
        created_at: Timestamp when record was created (inherited)
        updated_at: Timestamp when record was last updated (inherited)
    """
    
    __tablename__ = "documents"
    
    parcel_id = Column(
        CHAR(36),
        ForeignKey("parcels.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Foreign key to parcel (optional)"
    )
    
    document_type_id = Column(
        CHAR(36),
        ForeignKey("document_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Foreign key to document type"
    )
    
    filename = Column(
        String(500),
        nullable=False,
        comment="Original filename"
    )
    
    file_path = Column(
        String(500),
        nullable=False,
        unique=True,
        comment="Path to file on filesystem"
    )
    
    file_size_bytes = Column(
        Integer,
        nullable=False,
        comment="Size of file in bytes"
    )
    
    mime_type = Column(
        String(100),
        nullable=False,
        comment="MIME type of file"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Document description"
    )
    
    document_date = Column(
        Date,
        nullable=True,
        comment="Document date (issue/recording date)"
    )
    
    reference_number = Column(
        String(200),
        nullable=True,
        index=True,
        comment="Official reference number"
    )
    
    page_count = Column(
        Integer,
        nullable=True,
        comment="Number of pages (for PDF)"
    )
    
    checksum = Column(
        String(64),  # SHA-256 hex digest
        nullable=False,
        comment="SHA-256 checksum for integrity"
    )
    
    # Relationships
    parcel = relationship(
        "Parcel",
        back_populates="documents"
    )
    
    document_type = relationship(
        "DocumentType",
        back_populates="documents"
    )
    
    physical_location = relationship(
        "PhysicalLocation",
        uselist=False,
        back_populates="document",
        cascade="all, delete-orphan"
    )
    
    # Indexes for search
    __table_args__ = (
        Index('idx_filename', 'filename'),
        Index('idx_reference_number', 'reference_number'),
        Index('idx_document_date', 'document_date'),
    )
    
    def __repr__(self):
        """String representation of Document instance."""
        return f"<Document(filename='{self.filename}', size={self.file_size_bytes})>"