"""
Physical Location and Storage Cabinet Schemas
Phase 2 — Section 3.2
Land Intelligence System
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ============ Physical Location Schemas ============

class PhysicalLocationBase(BaseModel):
    """
    Base schema for PhysicalLocation with shared fields.
    """
    document_id: Optional[str] = Field(None, description="Foreign key to document (optional)")
    name: str = Field(..., max_length=200, description="Location name")
    location_code: str = Field(..., max_length=50, description="Unique location code")
    building: Optional[str] = Field(None, max_length=100, description="Building name or number")
    floor: Optional[str] = Field(None, max_length=50, description="Floor level")
    room_number: Optional[str] = Field(None, max_length=50, description="Room number or identifier")
    description: Optional[str] = Field(None, description="Description of location and access instructions")
    environmental_notes: Optional[str] = Field(None, description="Notes about environmental conditions")
    access_restrictions: Optional[str] = Field(None, description="Access restrictions or security requirements")
    contact_person: Optional[str] = Field(None, max_length=200, description="Person responsible for this location")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Contact phone number")


class PhysicalLocationCreate(PhysicalLocationBase):
    """
    Schema for creating a new PhysicalLocation.
    Excludes id and timestamps.
    """
    pass


class PhysicalLocationUpdate(BaseModel):
    """
    Schema for updating an existing PhysicalLocation.
    All fields are optional for partial updates.
    """
    document_id: Optional[str] = Field(None, description="Foreign key to document")
    name: Optional[str] = Field(None, max_length=200, description="Location name")
    location_code: Optional[str] = Field(None, max_length=50, description="Unique location code")
    building: Optional[str] = Field(None, max_length=100, description="Building name or number")
    floor: Optional[str] = Field(None, max_length=50, description="Floor level")
    room_number: Optional[str] = Field(None, max_length=50, description="Room number or identifier")
    description: Optional[str] = Field(None, description="Description of location")
    environmental_notes: Optional[str] = Field(None, description="Notes about environmental conditions")
    access_restrictions: Optional[str] = Field(None, description="Access restrictions")
    contact_person: Optional[str] = Field(None, max_length=200, description="Person responsible")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Contact phone number")
    is_active: Optional[bool] = Field(None, description="Soft delete flag")


class PhysicalLocationResponse(PhysicalLocationBase):
    """
    Schema for returning PhysicalLocation data to API client.
    """
    id: str = Field(..., description="UUID primary key")
    is_active: bool = Field(..., description="Soft delete flag")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    updated_at: datetime = Field(..., description="Timestamp when record was last updated")
    
    # Optional nested relationship data
    document_filename: Optional[str] = Field(None, description="Document filename (when included)")
    storage_cabinets: Optional[List["StorageCabinetResponse"]] = Field(None, description="Storage cabinets in this location")
    
    model_config = ConfigDict(from_attributes=True)


# ============ Storage Cabinet Schemas ============

class StorageCabinetBase(BaseModel):
    """
    Base schema for StorageCabinet with shared fields.
    """
    physical_location_id: str = Field(..., description="Foreign key to physical location")
    cabinet_number: str = Field(..., max_length=50, description="Cabinet identifier")
    cabinet_type: str = Field("filing", max_length=50, description="Type of cabinet")
    description: Optional[str] = Field(None, description="Description of cabinet contents")
    row_number: Optional[int] = Field(None, ge=1, description="Row number within location")
    column_number: Optional[int] = Field(None, ge=1, description="Column number within location")
    max_capacity: Optional[int] = Field(None, ge=1, description="Maximum document capacity")


class StorageCabinetCreate(StorageCabinetBase):
    """
    Schema for creating a new StorageCabinet.
    Excludes id, timestamps, and current count.
    """
    pass


class StorageCabinetUpdate(BaseModel):
    """
    Schema for updating an existing StorageCabinet.
    All fields are optional for partial updates.
    """
    physical_location_id: Optional[str] = Field(None, description="Foreign key to physical location")
    cabinet_number: Optional[str] = Field(None, max_length=50, description="Cabinet identifier")
    cabinet_type: Optional[str] = Field(None, max_length=50, description="Type of cabinet")
    description: Optional[str] = Field(None, description="Description of cabinet contents")
    row_number: Optional[int] = Field(None, ge=1, description="Row number")
    column_number: Optional[int] = Field(None, ge=1, description="Column number")
    max_capacity: Optional[int] = Field(None, ge=1, description="Maximum capacity")
    current_count: Optional[int] = Field(None, ge=0, description="Current document count")
    is_active: Optional[bool] = Field(None, description="Soft delete flag")


class StorageCabinetResponse(StorageCabinetBase):
    """
    Schema for returning StorageCabinet data to API client.
    """
    id: str = Field(..., description="UUID primary key")
    current_count: int = Field(0, ge=0, description="Current number of documents stored")
    is_active: bool = Field(..., description="Soft delete flag")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    updated_at: datetime = Field(..., description="Timestamp when record was last updated")
    
    # Optional nested relationship data
    location_name: Optional[str] = Field(None, description="Physical location name (when included)")
    
    model_config = ConfigDict(from_attributes=True)


# ============ Physical Location Finder Schemas ============

class PhysicalLocationFinderRequest(BaseModel):
    """
    Schema for physical location finder request.
    """
    parcel_id: Optional[str] = Field(None, description="Parcel ID to find physical location for")
    document_id: Optional[str] = Field(None, description="Document ID to find physical location for")
    reference_number: Optional[str] = Field(None, description="Reference number to search")


class PhysicalLocationFinderResponse(BaseModel):
    """
    Schema for physical location finder response.
    """
    found: bool = Field(..., description="Whether physical location was found")
    parcel_id: Optional[str] = None
    parcel_number: Optional[str] = None
    document_id: Optional[str] = None
    document_filename: Optional[str] = None
    physical_location: Optional[PhysicalLocationResponse] = None
    storage_cabinet: Optional[StorageCabinetResponse] = None
    message: str = Field(..., description="Result message")


# Forward reference for circular import
PhysicalLocationResponse.model_rebuild()# app/schemas/physical_location_schema.py
