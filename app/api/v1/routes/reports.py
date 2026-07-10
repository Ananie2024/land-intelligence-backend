# app/api/v1/routes/reports.py
"""
Reports Export Routes
Land Intelligence System

API endpoints for generating reports in PDF and Excel formats.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import require_client_or_admin, get_current_user_id
from app.services.reports.reports_service import ReportsService

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /reports/tax/{parcel_id} - Tax report export
# ---------------------------------------------------------------------------

@router.get(
    "/tax/{parcel_id}",
    summary="Export tax report",
    description="Generate a tax assessment report for a parcel in PDF or Excel format.",
)
async def export_tax_report(
    parcel_id: str,
    format: str = Query("pdf", pattern="^(pdf|excel)$", description="Export format"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_client_or_admin),
):
    """Generate tax report for a parcel."""
    service = ReportsService(db)
    
    try:
        content = await service.generate_tax_report(parcel_id, format)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    
    media_type = "application/pdf" if format == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = f"tax-report-{parcel_id}.{format}"
    
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(content)),
        }
    )


# ---------------------------------------------------------------------------
# GET /reports/parcels - Parcels report export
# ---------------------------------------------------------------------------

@router.get(
    "/parcels",
    summary="Export parcels report",
    description="Generate a parcels report in PDF or Excel format. Optionally filter by parish.",
)
async def export_parcels_report(
    format: str = Query("pdf", pattern="^(pdf|excel)$", description="Export format"),
    parish_id: str = Query(None, description="Filter by parish UUID"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_client_or_admin),
):
    """Generate parcels report."""
    service = ReportsService(db)
    
    try:
        content = await service.generate_parcels_report(parish_id, format)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    
    media_type = "application/pdf" if format == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = "parcels-report" + (f"-parish-{parish_id}" if parish_id else "") + f".{format}"
    
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(content)),
        }
    )


# ---------------------------------------------------------------------------
# GET /reports/dashboard - Dashboard statistics report export
# ---------------------------------------------------------------------------

@router.get(
    "/dashboard",
    summary="Export dashboard statistics report",
    description="Generate a dashboard statistics report in PDF or Excel format.",
)
async def export_dashboard_report(
    format: str = Query("pdf", pattern="^(pdf|excel)$", description="Export format"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    """Generate dashboard statistics report."""
    service = ReportsService(db)
    
    try:
        content = await service.generate_dashboard_report(format)
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
    media_type = "application/pdf" if format == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = f"dashboard-report.{format}"
    
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(content)),
        }
    )