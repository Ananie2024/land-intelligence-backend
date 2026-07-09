# app/schemas/dashboard_schema.py
"""
Dashboard Statistics Schemas
Land Intelligence System

Schemas for dashboard statistics and system overview.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ParishStats(BaseModel):
    """Statistics for parishes."""
    total_parishes: int = Field(..., description="Total number of active parishes")
    total_parcels: int = Field(..., description="Total parcel count across all parishes")
    avg_parcels_per_parish: float = Field(..., description="Average parcels per parish")


class ParcelStats(BaseModel):
    """Statistics for parcels."""
    total_parcels: int = Field(..., description="Total number of active parcels")
    total_area_sqm: float = Field(..., description="Total area in square meters")
    total_valuation: float = Field(..., description="Total valuation amount")
    parcels_with_deeds: int = Field(..., description="Number of parcels with title deeds")


class UserStats(BaseModel):
    """Statistics for users."""
    total_users: int = Field(..., description="Total number of active users")
    admin_count: int = Field(..., description="Number of admin users")
    client_count: int = Field(..., description="Number of client users")
    viewer_count: int = Field(..., description="Number of viewer users")


class DocumentStats(BaseModel):
    """Statistics for documents."""
    total_documents: int = Field(..., description="Total number of active documents")
    total_size_bytes: int = Field(..., description="Total document size in bytes")


class DatabaseStats(BaseModel):
    """Statistics for database."""
    database_status: str = Field(..., description="Database connectivity status")
    database_version: Optional[str] = Field(None, description="Database version")


class SystemStats(BaseModel):
    """Combined system statistics for dashboard."""
    parishes: ParishStats
    parcels: ParcelStats
    users: UserStats
    documents: DocumentStats
    database: DatabaseStats

    model_config = {"from_attributes": True}


class HealthStatus(BaseModel):
    """System health status."""
    status: str = Field(..., description="Overall system status (healthy/degraded)")
    api: str = Field(..., description="API status")
    database: str = Field(..., description="Database status")
    version: str = Field(..., description="API version")