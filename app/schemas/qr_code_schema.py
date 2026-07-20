"""
QR Code Registry Schemas
Phase 2 — Section 3.2
Land Intelligence System
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime


class QRCodeBase(BaseModel):
    """
    Base schema for QRCodeRegistry with shared fields.
    """
    parcel_upi: Optional[str] = Field(None, description="Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390")
    document_id: Optional[str] = Field(None, description="Foreign key to document (optional)")
    code_type: str = Field(..., max_length=20, description="Type of entity (parcel, document)")
    data_payload: Dict[str, Any] = Field(default_factory=dict, description="JSON data encoded in QR code")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    extra_data: Optional[Dict[str, Any]] = Field(
        None,
        description="JSON field for additional attributes",
    )

    model_config = ConfigDict(populate_by_name=True)


class QRCodeCreate(QRCodeBase):
    """
    Schema for creating a new QRCodeRegistry entry.
    Excludes id, timestamps, and system-generated fields.
    """
    pass


class QRCodeUpdate(BaseModel):
    """
    Schema for updating an existing QR code.
    All fields are optional for partial updates.
    """
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    is_revoked: Optional[bool] = Field(None, description="Whether QR code has been revoked")
    extra_data: Optional[Dict[str, Any]] = Field(
        None,
        description="JSON field for additional attributes",
    )
    is_active: Optional[bool] = Field(None, description="Soft delete flag")

    model_config = ConfigDict(populate_by_name=True)


class QRCodeResponse(QRCodeBase):
    """
    Schema for returning QRCodeRegistry data to API client.
    Includes id, timestamps, and system-generated fields.
    """
    id: str = Field(..., description="UUID primary key")
    code: str = Field(..., description="Unique QR code string")
    file_path: str = Field(..., description="Path to QR code image file")
    last_accessed_at: Optional[datetime] = Field(None, description="Last time QR was scanned")
    access_count: int = Field(0, ge=0, description="Number of times QR has been accessed")
    is_revoked: bool = Field(False, description="Whether QR code has been revoked")
    is_active: bool = Field(..., description="Soft delete flag")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    updated_at: datetime = Field(..., description="Timestamp when record was last updated")
    
    # Optional nested relationship data
    upi: Optional[str] = Field(None, description="Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390")
    document_filename: Optional[str] = Field(None, description="Document filename (when included)")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class QRCodeGenerateRequest(BaseModel):
    """
    Schema for QR code generation request.
    """
    parcel_upi: Optional[str] = Field(None, description="Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390")
    document_id: Optional[str] = Field(None, description="Document ID to generate QR for")
    expires_days: Optional[int] = Field(None, ge=1, le=365, description="Expiration in days (None = permanent)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class QRCodeVerifyRequest(BaseModel):
    """
    Schema for QR code verification request.
    """
    code: str = Field(..., description="QR code string to verify")


class QRCodeVerifyResponse(BaseModel):
    """
    Schema for QR code verification response.
    """
    is_valid: bool = Field(..., description="Whether QR code is valid and not expired/revoked")
    code: str = Field(..., description="QR code string")
    code_type: str = Field(..., description="Type of entity")
    parcel_upi: Optional[str] = Field(None, description="Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390")
    document_id: Optional[str] = Field(None, description="Associated document ID")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    is_revoked: bool = Field(..., description="Whether QR code is revoked")
    data_payload: Optional[Dict[str, Any]] = Field(None, description="Decoded data payload")
    message: str = Field(..., description="Verification message")