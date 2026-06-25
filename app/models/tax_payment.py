# app/models/tax_payment.py
"""
Tax Payment Model
Phase 2 — Section 3.1
Land Intelligence System
"""

from sqlalchemy import Column, String, Float, ForeignKey, Date, Boolean, Text
from sqlalchemy import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from app.models.base import BaseModel


class TaxPayment(BaseModel):
    """
    Tax payment entity representing individual payment transactions.
    
    Attributes:
        id: UUID primary key (inherited from BaseModel)
        tax_record_id: Foreign key to tax record
        payment_amount: Amount paid in this transaction
        payment_date: Date of payment
        payment_method: Method of payment (e.g., "cash", "bank_transfer", "check")
        payment_reference: External payment reference number
        receipt_number: Generated receipt number
        received_by: Name/ID of person who received payment
        notes: Additional notes about payment
        is_reversal: Whether this is a reversal of a previous payment
        reversed_payment_id: Reference to reversed payment (if is_reversal=True)
        is_active: Soft delete flag (inherited from BaseModel)
        created_at: Timestamp when record was created (inherited)
        updated_at: Timestamp when record was last updated (inherited)
    """
    
    __tablename__ = "tax_payments"
    
    tax_record_id = Column(UUID(as_uuid=True),
        ForeignKey("tax_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to tax record"
    )
    
    payment_amount = Column(
        Float,
        nullable=False,
        comment="Amount paid in this transaction"
    )
    
    payment_date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Date of payment"
    )
    
    payment_method = Column(
        String(50),
        nullable=False,
        comment="Method of payment (cash, bank_transfer, check)"
    )
    
    payment_reference = Column(
        String(100),
        nullable=True,
        index=True,
        comment="External payment reference number"
    )
    
    receipt_number = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Generated receipt number"
    )
    
    received_by = Column(
        String(200),
        nullable=False,
        comment="Name/ID of person who received payment"
    )
    
    notes = Column(
        Text,
        nullable=True,
        comment="Additional notes about payment"
    )
    
    is_reversal = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        comment="Whether this is a reversal of a previous payment"
    )
    
    reversed_payment_id = Column(UUID(as_uuid=True),
        ForeignKey("tax_payments.id", ondelete="SET NULL"),
        nullable=True,
        comment="Reference to reversed payment (if is_reversal=True)"
    )
    
    # Relationships
    tax_record = relationship(
        "TaxRecord",
        back_populates="payments"
    )
    
    reversed_payment = relationship(
        "TaxPayment",
        remote_side="TaxPayment.id",
        foreign_keys=[reversed_payment_id]
    )
    
    # Indexes for search
    __table_args__ = (
        Index('idx_payment_date', 'payment_date'),
        Index('idx_payment_method', 'payment_method'),
        Index('idx_receipt_number', 'receipt_number'),
    )
    
    def __repr__(self):
        """String representation of TaxPayment instance."""
        return f"<TaxPayment(amount={self.payment_amount}, date={self.payment_date}, receipt='{self.receipt_number}')>"