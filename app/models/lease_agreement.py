# app/models/lease_agreement.py
"""
Lease Agreement Model
Land Intelligence System
"""

from sqlalchemy import Column, String, Text, Numeric, ForeignKey, Date, Index
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.enums import LeaseStatus, PaymentFrequency


class LeaseAgreement(BaseModel):
    """
    Lease agreement entity representing a land rental contract between the church/parish and a tenant.

    Attributes:
        id: UUID primary key (inherited from BaseModel)
        parcel_id: Foreign key to parcel
        lease_number: Unique agreement code (e.g., LEASE-2026-0001)
        tenant_name: Full name of tenant (Individual or Enterprise)
        tenant_contact: Contact phone / email / address
        tenant_id_number: ID card / Passport / Registration number
        start_date: Lease contract start date
        end_date: Lease contract end date
        annual_rent_amount: Total annual rental fee
        payment_frequency: Installment breakdown (monthly, quarterly, semi_annually, annually)
        installment_amount: Calculated fee per payment period
        status: Agreement status (draft, active, expired, terminated, renewed)
        purpose_use: Description of land use under lease (e.g. Agriculture, Commercial)
        notes: Additional contract terms or remarks
        is_active: Soft delete flag (inherited)
        created_at: Creation timestamp (inherited)
        updated_at: Update timestamp (inherited)
    """

    __tablename__ = "lease_agreements"

    parcel_id = Column(
        UUID(as_uuid=True),
        ForeignKey("parcels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to parcel",
    )

    lease_number = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique lease agreement reference number",
    )

    tenant_name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Name of tenant",
    )

    tenant_contact = Column(
        String(255),
        nullable=True,
        comment="Tenant phone number, email, or address",
    )

    tenant_id_number = Column(
        String(100),
        nullable=True,
        comment="Tenant ID card / Passport / Tax ID",
    )

    start_date = Column(
        Date,
        nullable=False,
        comment="Lease start date",
    )

    end_date = Column(
        Date,
        nullable=False,
        comment="Lease end date",
    )

    annual_rent_amount = Column(
        Numeric(15, 2),
        nullable=False,
        default=0.00,
        server_default="0.00",
        comment="Annual rental amount in RWF/Currency",
    )

    payment_frequency = Column(
        SQLEnum(
            PaymentFrequency,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=PaymentFrequency.ANNUALLY,
        server_default="annually",
        comment="Frequency of payments",
    )

    installment_amount = Column(
        Numeric(15, 2),
        nullable=False,
        default=0.00,
        server_default="0.00",
        comment="Calculated installment amount per payment period",
    )

    status = Column(
        SQLEnum(
            LeaseStatus,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=LeaseStatus.ACTIVE,
        server_default="active",
        index=True,
        comment="Status of lease agreement",
    )

    purpose_use = Column(
        String(500),
        nullable=True,
        comment="Intended purpose of land use",
    )

    notes = Column(
        Text,
        nullable=True,
        comment="Additional notes and terms",
    )

    # Relationships
    parcel = relationship(
        "Parcel",
        back_populates="lease_agreements",
    )

    payment_schedules = relationship(
        "LeasePaymentSchedule",
        back_populates="lease_agreement",
        cascade="all, delete-orphan",
        order_by="LeasePaymentSchedule.due_date",
    )

    __table_args__ = (
        Index("idx_lease_number", "lease_number"),
        Index("idx_tenant_name", "tenant_name"),
        Index("idx_lease_status", "status"),
        Index("idx_lease_start_end", "start_date", "end_date"),
    )

    def __repr__(self):
        return f"<LeaseAgreement(number='{self.lease_number}', tenant='{self.tenant_name}', status='{self.status}')>"
