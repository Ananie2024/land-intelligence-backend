# app/models/document_type.py
"""
Document Type Model
Phase 2 — Section 3.1
Land Intelligence System
"""

from sqlalchemy import Column, String, Text, Boolean, text
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from app.models.base import BaseModel


class DocumentType(BaseModel):
    """
    Document type entity representing categories of documents.
    
    Attributes:
        id: UUID primary key (inherited from BaseModel)
        name: Type name (e.g., "Title Deed", "Survey Map")
        code: Unique type code (e.g., "TITLE", "MAP")
        description: Description of document type
        requires_verification: Whether documents of this type require verification
        retention_years: Retention period in years or 'PERMANENT'
        is_active: Soft delete flag (inherited from BaseModel)
        created_at: Timestamp when record was created (inherited)
        updated_at: Timestamp when record was last updated (inherited)
    """
    
    __tablename__ = "document_types"
    
    name = Column(
        String(100),
        nullable=False,
        comment="Type name (e.g., 'Title Deed', 'Survey Map')"
    )
    
    code = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique type code (e.g., 'TITLE', 'MAP')"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Description of document type"
    )
    
    requires_verification = Column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        comment="Whether documents of this type require verification"
    )
    
    retention_years = Column(
        String(10),
        nullable=False,
        server_default=text("'PERMANENT'"),
        comment="Retention period in years or 'PERMANENT'"
    )
    
    # Relationships
    documents = relationship(
        "Document",
        back_populates="document_type",
    )
    
    # Indexes for search
    __table_args__ = (
        Index('ix_document_types_name', 'name'),
    )
    
    def __repr__(self):
        """String representation of DocumentType instance."""
        return f"<DocumentType(name='{self.name}', code='{self.code}')>"