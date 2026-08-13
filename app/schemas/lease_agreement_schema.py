# app/schemas/lease_agreement_schema.py
"""
Lease Agreement & Payment Schedule Schemas
Land Intelligence System
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import LeaseStatus, PaymentFrequency, LeasePaymentStatus


# ------------------------------------------------------------------
# Lease Payment Schedule Schemas
# ------------------------------------------------------------------

class LeasePaymentScheduleBase(BaseModel):
    due_date: date
    amount_due: Decimal = Field(gt=0, description="Amount due for period")
    notes: Optional[str] = None


class LeasePaymentScheduleCreate(LeasePaymentScheduleBase):
    pass


class LeasePaymentRecordRequest(BaseModel):
    amount_paid: Decimal = Field(gt=0, description="Amount paid")
    paid_date: Optional[date] = Field(default_factory=date.today)
    payment_reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class LeasePaymentScheduleResponse(LeasePaymentScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lease_id: UUID
    amount_paid: Decimal
    status: LeasePaymentStatus
    paid_date: Optional[date] = None
    payment_reference: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ------------------------------------------------------------------
# Lease Agreement Schemas
# ------------------------------------------------------------------

class LeaseAgreementBase(BaseModel):
    parcel_id: UUID
    lease_number: Optional[str] = Field(None, description="Optional custom lease number; auto-generated if omitted")
    tenant_name: str = Field(..., min_length=2, max_length=255)
    tenant_contact: Optional[str] = Field(None, max_length=255)
    tenant_id_number: Optional[str] = Field(None, max_length=100)
    start_date: date
    end_date: date
    annual_rent_amount: Decimal = Field(..., gt=0, description="Annual rent amount in local currency")
    payment_frequency: PaymentFrequency = PaymentFrequency.ANNUALLY
    purpose_use: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class LeaseAgreementCreate(LeaseAgreementBase):
    auto_generate_schedules: bool = Field(True, description="Whether to automatically generate installment schedules")


class LeaseAgreementUpdate(BaseModel):
    tenant_name: Optional[str] = Field(None, min_length=2, max_length=255)
    tenant_contact: Optional[str] = Field(None, max_length=255)
    tenant_id_number: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    annual_rent_amount: Optional[Decimal] = Field(None, gt=0)
    payment_frequency: Optional[PaymentFrequency] = None
    status: Optional[LeaseStatus] = None
    purpose_use: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class ParcelMiniResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    upi: str
    owner_name: str
    location_description: Optional[str] = None


class LeaseAgreementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    parcel_id: UUID
    lease_number: str
    tenant_name: str
    tenant_contact: Optional[str] = None
    tenant_id_number: Optional[str] = None
    start_date: date
    end_date: date
    annual_rent_amount: Decimal
    payment_frequency: PaymentFrequency
    installment_amount: Decimal
    status: LeaseStatus
    purpose_use: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    parcel: Optional[ParcelMiniResponse] = None


class LeaseAgreementDetailResponse(LeaseAgreementResponse):
    payment_schedules: List[LeasePaymentScheduleResponse] = []


class LeaseSummaryStats(BaseModel):
    total_leases: int
    active_leases: int
    expired_leases: int
    draft_leases: int
    total_annual_revenue: Decimal
    total_collected_revenue: Decimal
    total_pending_revenue: Decimal
    overdue_payments_count: int
