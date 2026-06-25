# app/models/tax_record.py
"""
Tax Record Model
Phase 2 — Section 3.1
Land Intelligence System
"""

from sqlalchemy import Column, String, Float, ForeignKey, Date
from sqlalchemy import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from app.models.base import BaseModel


class TaxRecord(BaseModel):
    """
    Tax record entity representing annual tax assessment per parcel.
    
    Attributes:
        id: UUID primary key (inherited from BaseModel)
        parcel_id: Foreign key to parcel
        assessment_year: Year of tax assessment (e.g., "2024")
        assessed_value: Assessed value of parcel for tax purposes
        tax_rate_applied: Tax rate applied for this assessment
        base_tax_amount: Base tax amount calculated
        penalties_amount: Penalties amount if any
        total_amount: Total tax amount due (base + penalties)
        status: Status of tax record (e.g., "pending", "paid", "overdue")
        due_date: Due date for payment
        paid_date: Date when fully paid (if applicable)
        payment_reference: Reference for full payment
        notes: Additional notes about tax assessment
        is_active: Soft delete flag (inherited from BaseModel)
        created_at: Timestamp when record was created (inherited)
        updated_at: Timestamp when record was last updated (inherited)
    """
    
    __tablename__ = "tax_records"
    
    parcel_id = Column(UUID(as_uuid=True),
        ForeignKey("parcels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to parcel"
    )
    
    assessment_year = Column(
        String(4),  # YYYY format
        nullable=False,
        index=True,
        comment="Year of tax assessment (e.g., '2024')"
    )
    
    assessed_value = Column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0",
        comment="Assessed value of parcel for tax purposes"
    )
    
    tax_rate_applied = Column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0",
        comment="Tax rate applied for this assessment"
    )
    
    base_tax_amount = Column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0",
        comment="Base tax amount calculated"
    )
    
    penalties_amount = Column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0",
        comment="Penalties amount if any"
    )
    
    total_amount = Column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0",
        comment="Total tax amount due (base + penalties)"
    )
    
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
        comment="Status of tax record (pending, paid, overdue)"
    )
    
    due_date = Column(
        Date,
        nullable=False,
        comment="Due date for payment"
    )
    
    paid_date = Column(
        Date,
        nullable=True,
        comment="Date when fully paid (if applicable)"
    )
    
    payment_reference = Column(
        String(100),
        nullable=True,
        comment="Reference for full payment"
    )
    
    notes = Column(
        String(500),
        nullable=True,
        comment="Additional notes about tax assessment"
    )
    
    # Relationships
    parcel = relationship(
        "Parcel",
        back_populates="tax_records"
    )
    
    payments = relationship(
        "TaxPayment",
        back_populates="tax_record",
        cascade="all, delete-orphan"
    )
    
    # Indexes for search and unique constraint
    __table_args__ = (
        Index('idx_assessment_year', 'assessment_year'),
        Index('idx_status', 'status'),
        Index('idx_due_date', 'due_date'),
        # Ensure only one tax record per parcel per year
        Index('idx_unique_parcel_year', 'parcel_id', 'assessment_year', unique=True),
    )
    
    def __repr__(self):
        """String representation of TaxRecord instance."""
        return f"<TaxRecord(parcel={self.parcel_id}, year={self.assessment_year}, total={self.total_amount})>"