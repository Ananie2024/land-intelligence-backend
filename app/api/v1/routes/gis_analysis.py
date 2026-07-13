# app/api/v1/routes/gis_analysis.py
"""
GIS Analysis Route Endpoints
Phase 3 — Section 4.2
Land Intelligence System
"""

import logging
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id
from app.services.gis.gis_service import GisAnalysisService
from app.schemas.gis_analysis_schema import (
    DistanceRequest,
    DistanceResponse,
    IntersectionRequest,
    IntersectionResponse,
    ContainsPointRequest,
    ContainsPointResponse,
    OverlayRequest,
    OverlayResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/distance",
    response_model=DistanceResponse,
    summary="Calculate distance between geometries",
    description="Calculate minimum distance in meters between two geometries or parcels."
)
async def calculate_distance(
    payload: DistanceRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        service = GisAnalysisService(db)
        result = await service.calculate_distance(
            payload.geom1_wkt,
            payload.parcel_upi_1,
            payload.geom2_wkt,
            payload.parcel_upi_2
        )
        
        return DistanceResponse(
            distance_meters=result["distance_meters"],
            message=result["message"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error calculating distance: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal spatial computation error: {str(e)}"
        )


@router.post(
    "/intersects",
    response_model=IntersectionResponse,
    summary="Check intersection and overlap",
    description="Determine if two geometries intersect/overlap, and compute the overlapping area and percentages."
)
async def check_intersection(
    payload: IntersectionRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        service = GisAnalysisService(db)
        result = await service.check_intersection(
            payload.geom1_wkt,
            payload.parcel_upi_1,
            payload.geom2_wkt,
            payload.parcel_upi_2
        )
        
        return IntersectionResponse(
            intersects=result["intersects"],
            overlaps=result["overlaps"],
            intersection_area_sqm=result["intersection_area_sqm"],
            percentage_overlap_geom1=result["percentage_overlap_geom1"],
            percentage_overlap_geom2=result["percentage_overlap_geom2"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error calculating intersection: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal spatial computation error: {str(e)}"
        )


@router.post(
    "/contains-point",
    response_model=ContainsPointResponse,
    summary="Check point containment",
    description="Verify if a geometry or parcel contains or intersects a given latitude/longitude point."
)
async def contains_point(
    payload: ContainsPointRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        service = GisAnalysisService(db)
        result = await service.contains_point(
            payload.geom_wkt,
            payload.parcel_upi,
            payload.x,
            payload.y
        )
        
        return ContainsPointResponse(
            contains=result["contains"],
            intersects=result["intersects"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error checking point containment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal spatial computation error: {str(e)}"
        )


@router.post(
    "/check-overlay",
    response_model=OverlayResponse,
    summary="Check zoning overlay compliance",
    description="Overlay a parcel on a zoning district geometry to verify zoning code overlay and compliance area."
)
async def check_zoning_overlay(
    payload: OverlayRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        service = GisAnalysisService(db)
        result = await service.check_zoning_overlay(
            payload.parcel_upi,
            payload.zoning_wkt,
            payload.zoning_code
        )
        
        return OverlayResponse(
            intersects=result["intersects"],
            intersection_area=result["intersection_area"],
            percentage_overlap=result["percentage_overlap"],
            zoning_code=result["zoning_code"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error checking zoning overlay compliance: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal zoning check error: {str(e)}"
        )