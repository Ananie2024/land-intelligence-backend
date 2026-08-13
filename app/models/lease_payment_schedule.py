# app/models/lease_payment_schedule.py
"""
Lease Payment Schedule Model
Land Intelligence System
"""

from sqlalchemy import Column, String, Text, Numeric, ForeignKey, Date, Index
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.enums import LeasePaymentStatus


class LeasePaymentSchedule(BaseModel):
    """
    Lease payment schedule item tracking planned and recorded installment payments for a lease agreement.

    Attributes:
        id: UUID primary key (inherited from BaseModel)
        lease_id: Foreign key to lease_agreements
        due_date: Payment due date
        amount_due: Expected installment payment amount
        amount_paid: Actual paid amount
        status: Payment status (pending, paid, overdue, partial, cancelled)
        paid_date: Date payment was recorded
        payment_reference: Bank transaction reference / receipt number
        notes: Payment remarks
    """

    __tablename__ = "lease_payment_schedules"

    lease_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lease_agreements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to lease_agreements",
    )

    due_date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Payment due date",
    )

    amount_due = Column(
        Numeric(15, 2),
        nullable=False,
        default=0.00,
        server_default="0.00",
        comment="Amount due for this period",
    )

    amount_paid = Column(
        Numeric(15, 2),
        nullable=False,
        default=0.00,
        server_default="0.00",
        comment="Amount paid to date",
    )

    status = Column(
        SQLEnum(
            LeasePaymentStatus,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=LeasePaymentStatus.PENDING,
        server_default="pending",
        index=True,
        comment="Status of payment",
    )

    paid_date = Column(
        Date,
        nullable=True,
        comment="Date payment was fulfilled",
    )

    payment_reference = Column(
        String(100),
        nullable=True,
        comment="Payment transaction or receipt reference",
    )

    notes = Column(
        Text,
        nullable=True,
        comment="Payment notes",
    )

    # Relationship
    lease_agreement = relationship(
        "LeaseAgreement",
        back_populates="payment_schedules",
    )

    __table_args__ = (
        Index("idx_lease_schedule_due", "lease_id", "due_date"),
        Index("idx_lease_schedule_status", "status"),
    )

    def __repr__(self):
        return f"<LeasePaymentSchedule(lease='{self.lease_id}', due='{self.due_date}', status='{self.status}')>"
