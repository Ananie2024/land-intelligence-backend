# app/api/v1/routes/dashboard.py
"""
Dashboard Routes
Land Intelligence System

API endpoints for dashboard statistics and system overview.
"""

import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id
from app.services.dashboard.dashboard_service import DashboardService
from app.schemas.dashboard_schema import SystemStats, ParishStats, ParcelStats, UserStats

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /dashboard/stats — system statistics
# ---------------------------------------------------------------------------

@router.get(
    "/stats",
    response_model=SystemStats,
    status_code=status.HTTP_200_OK,
    summary="Get system statistics",
    description="Return comprehensive system statistics for the dashboard including parishes, parcels, users, and documents.",
)
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    """Get all system statistics for the dashboard."""
    service = DashboardService(db)
    return await service.get_system_stats()


# ---------------------------------------------------------------------------
# GET /dashboard/stats/parishes — parish statistics
# ---------------------------------------------------------------------------

@router.get(
    "/stats/parishes",
    response_model=ParishStats,
    status_code=status.HTTP_200_OK,
    summary="Get parish statistics",
    description="Return statistics for parishes including total count and parcel counts.",
)
async def get_parish_stats(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    """Get parish statistics only."""
    service = DashboardService(db)
    return await service.get_parish_stats()


# ---------------------------------------------------------------------------
# GET /dashboard/stats/parcels — parcel statistics
# ---------------------------------------------------------------------------

@router.get(
    "/stats/parcels",
    response_model=ParcelStats,
    status_code=status.HTTP_200_OK,
    summary="Get parcel statistics",
    description="Return statistics for parcels including total count, area, and valuation.",
)
async def get_parcel_stats(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    """Get parcel statistics only."""
    service = DashboardService(db)
    return await service.get_parcel_stats()


# ---------------------------------------------------------------------------
# GET /dashboard/stats/users — user statistics
# ---------------------------------------------------------------------------

@router.get(
    "/stats/users",
    response_model=UserStats,
    status_code=status.HTTP_200_OK,
    summary="Get user statistics",
    description="Return statistics for users including total count and role breakdowns.",
)
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    """Get user statistics only."""
    service = DashboardService(db)
    return await service.get_user_stats()