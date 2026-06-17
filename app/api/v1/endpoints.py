# app/api/v1/endpoints.py

"""
API v1 Router
Land Intelligence System
"""

from fastapi import APIRouter, Depends

from app.api.logging_dependencies import correlation_id_logging
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
)

# Apply logging globally to v1
router = APIRouter(dependencies=[Depends(correlation_id_logging)])

# Health endpoint (Public but logged)
@router.get("/health", tags=["system"])
async def api_health():
    return {
        "status": "healthy",
        "api_version": "v1"
    }


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
