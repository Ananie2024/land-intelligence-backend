# app/schemas/tax_schema.py
"""
Tax Record and Tax Payment Schemas
Phase 2 — Section 3.2
Land Intelligence System
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date


# ============ Tax Record Schemas ============

class TaxRecordBase(BaseModel):
    """
    Base schema for TaxRecord with shared fields.
    """
    parcel_upi: str = Field(..., description="Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390")
    assessment_year: str = Field(..., pattern=r"^\d{4}$", description="Year of tax assessment")
    assessed_value: float = Field(..., ge=0, description="Assessed value of parcel for tax purposes")
    tax_rate_applied: float = Field(..., ge=0, description="Tax rate applied for this assessment")
    base_tax_amount: float = Field(..., ge=0, description="Base tax amount calculated")
    penalties_amount: float = Field(0, ge=0, description="Penalties amount if any")
    total_amount: float = Field(..., ge=0, description="Total tax amount due (base + penalties)")
    due_date: date = Field(..., description="Due date for payment")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes about tax assessment")


class TaxRecordCreate(TaxRecordBase):
    """
    Schema for creating a new TaxRecord.
    Excludes id, timestamps, and derived fields.
    """
    pass


class TaxRecordUpdate(BaseModel):
    """
    Schema for updating an existing TaxRecord.
    All fields are optional for partial updates.
    """
    assessed_value: Optional[float] = Field(None, ge=0, description="Assessed value")
    tax_rate_applied: Optional[float] = Field(None, ge=0, description="Tax rate applied")
    base_tax_amount: Optional[float] = Field(None, ge=0, description="Base tax amount")
    penalties_amount: Optional[float] = Field(None, ge=0, description="Penalties amount")
    total_amount: Optional[float] = Field(None, ge=0, description="Total tax amount due")
    status: Optional[str] = Field(None, description="Status (pending, paid, overdue)")
    due_date: Optional[date] = Field(None, description="Due date for payment")
    paid_date: Optional[date] = Field(None, description="Date when fully paid")
    payment_reference: Optional[str] = Field(None, max_length=100, description="Reference for full payment")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    is_active: Optional[bool] = Field(None, description="Soft delete flag")


class TaxRecordResponse(TaxRecordBase):
    """
    Schema for returning TaxRecord data to API client.
    """
    id: str = Field(..., description="UUID primary key")
    status: str = Field(..., description="Status (pending, paid, overdue)")
    paid_date: Optional[date] = Field(None, description="Date when fully paid")
    payment_reference: Optional[str] = Field(None, max_length=100, description="Reference for full payment")
    is_active: bool = Field(..., description="Soft delete flag")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    updated_at: datetime = Field(..., description="Timestamp when record was last updated")
    
    # Optional nested relationship data
    upi: Optional[str] = Field(None, description="Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390")
    payments: Optional[List["TaxPaymentResponse"]] = Field(None, description="Payment transactions")
    
    model_config = ConfigDict(from_attributes=True)


# ============ Tax Payment Schemas ============

class TaxPaymentBase(BaseModel):
    """
    Base schema for TaxPayment with shared fields.
    """
    tax_record_id: str = Field(..., description="Foreign key to tax record")
    payment_amount: float = Field(..., gt=0, description="Amount paid in this transaction")
    payment_date: date = Field(..., description="Date of payment")
    payment_method: str = Field(..., max_length=50, description="Method of payment")
    payment_reference: Optional[str] = Field(None, max_length=100, description="External payment reference")
    received_by: str = Field(..., max_length=200, description="Name/ID of person who received payment")
    notes: Optional[str] = Field(None, description="Additional notes about payment")


class TaxPaymentCreate(TaxPaymentBase):
    """
    Schema for creating a new TaxPayment.
    Excludes id, timestamps, and generated receipt number.
    """
    pass


class TaxPaymentUpdate(BaseModel):
    """
    Schema for updating an existing TaxPayment.
    All fields are optional for partial updates.
    """
    payment_amount: Optional[float] = Field(None, gt=0, description="Amount paid")
    payment_date: Optional[date] = Field(None, description="Date of payment")
    payment_method: Optional[str] = Field(None, max_length=50, description="Method of payment")
    payment_reference: Optional[str] = Field(None, max_length=100, description="External payment reference")
    notes: Optional[str] = Field(None, description="Additional notes")
    is_active: Optional[bool] = Field(None, description="Soft delete flag")


class TaxPaymentResponse(TaxPaymentBase):
    """
    Schema for returning TaxPayment data to API client.
    """
    id: str = Field(..., description="UUID primary key")
    receipt_number: str = Field(..., description="Generated receipt number")
    is_reversal: bool = Field(..., description="Whether this is a reversal")
    reversed_payment_id: Optional[str] = Field(None, description="Reference to reversed payment")
    is_active: bool = Field(..., description="Soft delete flag")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    updated_at: datetime = Field(..., description="Timestamp when record was last updated")
    
    model_config = ConfigDict(from_attributes=True)


# ============ Tax Calculation Schemas ============

class TaxCalculationRequest(BaseModel):
    """
    Schema for tax calculation request.
    """
    parcel_upi: str = Field(..., description="Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390")
    assessment_year: str = Field(..., pattern=r"^\d{4}$", description="Assessment year")
    land_use_category_id: Optional[str] = Field(None, description="Override land use category")
    include_penalties: bool = Field(True, description="Include late payment penalties")


class TaxCalculationResponse(BaseModel):
    """
    Schema for tax calculation response.
    """
    parcel_upi: str
    upi: str
    assessment_year: str
    land_use_category_name: str
    area_sqm: float
    assessed_value: float
    tax_rate: float
    base_tax_amount: float
    penalties_amount: float
    total_amount: float
    due_date: date


class TaxPaymentRequest(BaseModel):
    """
    Schema for recording a payment.
    """
    tax_record_id: str = Field(..., description="Tax record ID")
    payment_amount: float = Field(..., gt=0, description="Amount to pay")
    payment_date: date = Field(..., description="Date of payment")
    payment_method: str = Field(..., max_length=50, description="Method of payment")
    payment_reference: Optional[str] = Field(None, max_length=100, description="External payment reference")
    notes: Optional[str] = Field(None, description="Additional notes")


class OutstandingBalanceResponse(BaseModel):
    """
    Schema for outstanding balance response.
    """
    parcel_upi: str
    upi: str
    total_outstanding: float
    overdue_amount: float
    upcoming_amount: float
    records: List[TaxRecordResponse]


# Forward reference for circular import
TaxRecordResponse.model_rebuild()