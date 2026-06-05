# app/api/v1/endpoints.py

"""
API v1 Router
Land Intelligence System
"""

from fastapi import APIRouter

from app.api.v1.routes import (
    parishes,
    parcels,
    documents,
    gis_analysis,
    tax_calculations,
    qr_codes,
    physical_locations,
    backups,
)

router = APIRouter()

# Health endpoint
@router.get("/health", tags=["system"])
async def api_health():
    return {
        "status": "healthy",
        "api_version": "v1"
    }


# Register feature routers
router.include_router(
    parishes.router,
    prefix="/parishes",
    tags=["Parishes"]
)

router.include_router(
    parcels.router,
    prefix="/parcels",
    tags=["Parcels"]
)

router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"]
)

router.include_router(
    gis_analysis.router,
    prefix="/gis",
    tags=["GIS Analysis"]
)

router.include_router(
    tax_calculations.router,
    prefix="/tax",
    tags=["Tax Calculations"]
)

router.include_router(
    qr_codes.router,
    prefix="/qr",
    tags=["QR Codes"]
)

router.include_router(
    physical_locations.router,
    prefix="/locations",
    tags=["Physical Locations"]
)

router.include_router(
    backups.router,
    prefix="/backups",
    tags=["Backups"]
)