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
from shapely import wkt
from shapely.geometry.base import BaseGeometry

from app.core.database import get_db
from app.repositories.parcel_repository import ParcelRepository
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
from app.services.gis import spatial_analyzer, polygon_intersection, masterplan_overlay

logger = logging.getLogger(__name__)

router = APIRouter()

async def _resolve_geometry(
    db: AsyncSession,
    geom_wkt: Optional[str],
    parcel_id: Optional[str],
    param_name: str
) -> BaseGeometry:
    """
    Helper to resolve a geometry from either a WKT string or a parcel ID from database.
    """
    if geom_wkt:
        try:
            return wkt.loads(geom_wkt)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid WKT format for {param_name}: {str(e)}"
            )
            
    if parcel_id:
        repo = ParcelRepository(db)
        parcel = await repo.get(parcel_id)
        if not parcel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parcel with ID '{parcel_id}' not found for {param_name}."
            )
        if not parcel.geometry_wkb:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parcel '{parcel_id}' does not have spatial geometry data."
            )
        return spatial_analyzer.ensure_geometry(parcel.geometry_wkb)
        
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Either WKT or parcel ID must be specified for {param_name}."
    )

@router.post(
    "/distance",
    response_model=DistanceResponse,
    summary="Calculate distance between geometries",
    description="Calculate minimum distance in meters between two geometries or parcels."
)
async def calculate_distance(
    payload: DistanceRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        geom1 = await _resolve_geometry(db, payload.geom1_wkt, payload.parcel_id_1, "geom1 / parcel_id_1")
        geom2 = await _resolve_geometry(db, payload.geom2_wkt, payload.parcel_id_2, "geom2 / parcel_id_2")
        
        distance = spatial_analyzer.calculate_distance(geom1, geom2)
        
        return DistanceResponse(
            distance_meters=distance,
            message="Distance calculated successfully using metric EPSG:21035 CRS (Rwanda)."
        )
    except HTTPException:
        raise
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
    db: AsyncSession = Depends(get_db)
):
    try:
        geom1 = await _resolve_geometry(db, payload.geom1_wkt, payload.parcel_id_1, "geom1 / parcel_id_1")
        geom2 = await _resolve_geometry(db, payload.geom2_wkt, payload.parcel_id_2, "geom2 / parcel_id_2")
        
        # Geometries must be projected to a metric CRS for area calculations
        from app.utils.coordinate_transformations import to_metric
        metric_g1 = to_metric(geom1)
        metric_g2 = to_metric(geom2)
        
        intersects = metric_g1.intersects(metric_g2)
        overlaps = polygon_intersection.detect_overlap(metric_g1, metric_g2)
        
        intersection_area = polygon_intersection.calculate_intersection_area(metric_g1, metric_g2)
        
        g1_area = metric_g1.area
        g2_area = metric_g2.area
        
        percentage_g1 = (intersection_area / g1_area * 100.0) if g1_area > 0 else 0.0
        percentage_g2 = (intersection_area / g2_area * 100.0) if g2_area > 0 else 0.0
        
        return IntersectionResponse(
            intersects=intersects,
            overlaps=overlaps,
            intersection_area_sqm=round(intersection_area, 2),
            percentage_overlap_geom1=round(percentage_g1, 2),
            percentage_overlap_geom2=round(percentage_g2, 2)
        )
    except HTTPException:
        raise
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
    db: AsyncSession = Depends(get_db)
):
    try:
        geom = await _resolve_geometry(db, payload.geom_wkt, payload.parcel_id, "geom / parcel_id")
        point_tuple = (payload.x, payload.y)
        
        contains = spatial_analyzer.contains_point(geom, point_tuple)
        intersects = spatial_analyzer.intersects_point(geom, point_tuple)
        
        return ContainsPointResponse(
            contains=contains,
            intersects=intersects
        )
    except HTTPException:
        raise
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
    db: AsyncSession = Depends(get_db)
):
    try:
        parcel_geom = await _resolve_geometry(db, None, payload.parcel_id, "parcel_id")
        
        try:
            zoning_geom = wkt.loads(payload.zoning_wkt)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid WKT format for zoning_wkt: {str(e)}"
            )
            
        # Transform both geometries to metric CRS for accurate compliance calculation
        from app.utils.coordinate_transformations import to_metric
        metric_parcel = to_metric(parcel_geom)
        metric_zoning = to_metric(zoning_geom)
        
        res = masterplan_overlay.overlay_parcel_on_zoning(
            metric_parcel,
            metric_zoning,
            payload.zoning_code
        )
        
        return OverlayResponse(
            intersects=res["intersects"],
            intersection_area=res["intersection_area"],
            percentage_overlap=res["percentage_overlap"],
            zoning_code=res["zoning_code"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking zoning overlay compliance: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal zoning check error: {str(e)}"
        )
