# app/models/parcel_ownership_history.py
"""
Parcel Ownership History Model
Land Intelligence System
"""

from sqlalchemy import Column, String, Text, Date, ForeignKey, Index
from sqlalchemy import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ParcelOwnershipHistory(BaseModel):
    """
    Immutable ownership history for land parcels.
    Tracks changes in ownership over time.
    """

    __tablename__ = "parcel_ownership_history"

    parcel_id = Column(
        UUID(as_uuid=True),
        ForeignKey("parcels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to parcel"
    )

    owner_name = Column(
        String(500),
        nullable=False,
        comment="Name of the owner at this point in time"
    )

    owner_contact = Column(
        String(500),
        nullable=True,
        comment="Contact information for the owner"
    )

    transfer_date = Column(
        Date,
        nullable=False,
        comment="Date when ownership was transferred"
    )

    document_reference = Column(
        String(255),
        nullable=True,
        comment="Reference to supporting document (title deed, sale agreement, etc.)"
    )

    notes = Column(
        Text,
        nullable=True,
        comment="Additional notes about the ownership transfer"
    )

    # Relationships
    parcel = relationship(
        "Parcel",
        back_populates="ownership_history"
    )

    __table_args__ = (
        Index('idx_parcel_transfer_date', 'parcel_id', 'transfer_date'),
    )

    def __repr__(self):
        """String representation of ParcelOwnershipHistory instance."""
        return f"<ParcelOwnershipHistory(parcel_id={self.parcel_id}, owner='{self.owner_name}', date={self.transfer_date})>"