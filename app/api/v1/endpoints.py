"""
API v1 Endpoints Router
Phase 1 — Section 2.5
Land Intelligence System
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

# Create v1 router
router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint that verifies database connectivity.
    
    Returns:
        dict: Status of the API and database connection
    """
    db_status = "unhealthy"
    try:
        # Execute simple query to verify database connection
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        # Log error will be handled by middleware
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "api": "healthy",
        "database": db_status,
        "version": "1.0.0"
    }


# Placeholder for future route includes
# These will be implemented in Phase 3
# router.include_router(parishes.router, prefix="/parishes", tags=["parishes"])
# router.include_router(parcels.router, prefix="/parcels", tags=["parcels"])
# router.include_router(documents.router, prefix="/documents", tags=["documents"])
# router.include_router(gis_analysis.router, prefix="/gis", tags=["gis"])
# router.include_router(tax_calculations.router, prefix="/tax", tags=["tax"])
# router.include_router(qr_codes.router, prefix="/qr", tags=["qr"])
# router.include_router(physical_locations.router, prefix="/locations", tags=["locations"])
# router.include_router(backups.router, prefix="/backups", tags=["backups"])# app/api/v1/endpoints.py
