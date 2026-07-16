# app/api/v1/endpoints.py

"""
API v1 Router
Land Intelligence System
"""

import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.logging_dependencies import correlation_id_logging
from app.core.database import get_db
from app.core.token_blacklist import get_redis_client

from app.api.auth_dependencies import get_current_user_data
from app.api.v1.routes import (
    parishes,
    parcels,
    documents,
    gis_analysis,
    tax_calculations,
    qr_codes,
    physical_locations,
    backups,
    auth,
    users,
    dashboard,
    reports,
    settings,
)

# Apply logging globally to v1
router = APIRouter(dependencies=[Depends(correlation_id_logging)])
logger = logging.getLogger(__name__)

# Auth endpoints (Public)
router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"],
)

# Users endpoints (Admin managed)
router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_user_data)]
)

# Health endpoints (Public but logged)
@router.get("/health/live", tags=["system"])
async def health_live():
    """
    Liveness check to verify the API process is running.
    Returns 200 OK if the application is up, regardless of DB/Redis status.
    """
    return {"status": "alive"}


@router.get("/health/ready", tags=["system"])
async def health_ready(db: AsyncSession = Depends(get_db)):
    """
    Readiness check to verify external dependencies (Database, Redis) are reachable.
    Returns 503 if any dependency is unavailable.
    """
    db_status = "unhealthy"
    redis_status = "unhealthy"

    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database v1 health check failed: {str(e)}")

    try:
        redis_client = get_redis_client()
        await redis_client.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis v1 health check failed: {str(e)}")

    is_ready = db_status == "healthy" and redis_status == "healthy"
    status_code = 200 if is_ready else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if is_ready else "unhealthy",
            "api": "healthy",
            "database": db_status,
            "redis": redis_status,
            "api_version": "v1",
        },
    )


@router.get("/health", tags=["system"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Fallback health check endpoint. Maps to readiness check for backwards compatibility.
    """
    return await health_ready(db)


# Register feature routers (Protected and logged)
router.include_router(
    parishes.router,
    prefix="/parishes",
    tags=["Parishes"],
    dependencies=[Depends(get_current_user_data)]
)

router.include_router(
    parcels.router,
    prefix="/parcels",
    tags=["Parcels"],
    dependencies=[Depends(get_current_user_data)]
)

router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
    dependencies=[Depends(get_current_user_data)]
)

router.include_router(
    gis_analysis.router,
    prefix="/gis",
    tags=["GIS Analysis"],
    dependencies=[Depends(get_current_user_data)]
)

router.include_router(
    tax_calculations.router,
    prefix="/tax",
    tags=["Tax Calculations"],
    dependencies=[Depends(get_current_user_data)]
)

router.include_router(
    qr_codes.router,
    prefix="/qr",
    tags=["QR Codes"],
    dependencies=[Depends(get_current_user_data)]
)

router.include_router(
    physical_locations.router,
    prefix="/locations",
    tags=["Physical Locations"],
    dependencies=[Depends(get_current_user_data)]
)

router.include_router(
    backups.router,
    prefix="/backups",
    tags=["Backups"],
    dependencies=[Depends(get_current_user_data)]
)

router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_user_data)]
)

router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(get_current_user_data)]
)

router.include_router(
    settings.router,
    prefix="/settings",
    tags=["Settings"],
    dependencies=[Depends(get_current_user_data)]
)