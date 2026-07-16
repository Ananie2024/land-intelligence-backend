"""
Parish Schemas
Phase 2 — Section 3.2
Land Intelligence System
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class ParishBase(BaseModel):
    """
    Base schema for Parish with shared fields.
    Simplified to only include parish name.
    """
    name: str = Field(..., max_length=200, description="Official parish name")


class ParishCreate(ParishBase):
    """
    Schema for creating a new Parish.
    """
    pass


class ParishUpdate(BaseModel):
    """
    Schema for updating an existing Parish.
    All fields are optional for partial updates.
    """
    name: Optional[str] = Field(None, max_length=200, description="Official parish name")
    is_active: Optional[bool] = Field(None, description="Soft delete flag")


class ParishResponse(ParishBase):
    """
    Schema for returning Parish data to API client.
    Includes id and timestamps.
    """
    id: str = Field(..., description="UUID primary key")
    is_active: bool = Field(..., description="Soft delete flag")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    updated_at: datetime = Field(..., description="Timestamp when record was last updated")
    
    model_config = ConfigDict(from_attributes=True)


class ParishListResponse(BaseModel):
    """
    Schema for paginated parish list response.
    """
    items: List[ParishResponse]
    total: int
    page: int
    size: int
    pages: int