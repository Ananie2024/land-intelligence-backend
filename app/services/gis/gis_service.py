# app/services/gis/gis_service.py
"""
GIS Analysis Service
Phase 3 — Section 4.2
Land Intelligence System
"""

import logging
from typing import Optional

from shapely import wkt
from shapely.geometry.base import BaseGeometry

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.parcel_repository import ParcelRepository
from app.services.gis.spatial_analyzer import ensure_geometry, calculate_distance, contains_point, intersects_point
from app.services.gis.polygon_intersection import detect_overlap, calculate_intersection_area
from app.services.gis.masterplan_overlay import overlay_parcel_on_zoning
from app.utils.coordinate_transformations import to_metric

logger = logging.getLogger(__name__)


class GisAnalysisService:
    """
    Business logic layer for GIS analysis operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.parcel_repo = ParcelRepository(db)

    async def _resolve_geometry(
        self,
        geom_wkt: Optional[str],
        parcel_upi: Optional[str],
        param_name: str
    ) -> BaseGeometry:
        """
        Resolve a geometry from either a WKT string or a parcel UPI from database.
        """
        if geom_wkt:
            try:
                return wkt.loads(geom_wkt)
            except Exception as e:
                raise ValueError(f"Invalid WKT format for {param_name}: {str(e)}")
            
        if parcel_upi:
            parcel = await self.parcel_repo.get_by_upi(parcel_upi)
            if not parcel:
                raise ValueError(f"Parcel with UPI '{parcel_upi}' not found for {param_name}.")
            if parcel.geometry_wkb is None:
                raise ValueError(f"Parcel '{parcel_upi}' does not have spatial geometry data.")
            return ensure_geometry(parcel.geometry_wkb)
            
        raise ValueError(f"Either WKT or parcel UPI must be specified for {param_name}.")

    async def calculate_distance(
        self,
        geom1_wkt: Optional[str],
        parcel_upi_1: Optional[str],
        geom2_wkt: Optional[str],
        parcel_upi_2: Optional[str]
    ):
        """
        Calculate minimum distance in meters between two geometries or parcels.
        
        Args:
            geom1_wkt: First geometry in WKT format (optional)
            parcel_upi_1: UPI of first parcel - e.g. 1/02/02/03/1390 (optional)
            geom2_wkt: Second geometry in WKT format (optional)
            parcel_upi_2: UPI of second parcel - e.g. 1/02/02/03/1390 (optional)
        """
        geom1 = await self._resolve_geometry(geom1_wkt, parcel_upi_1, "geom1 / parcel_upi_1")
        geom2 = await self._resolve_geometry(geom2_wkt, parcel_upi_2, "geom2 / parcel_upi_2")
        
        distance = calculate_distance(geom1, geom2)
        
        return {
            "distance_meters": distance,
            "message": "Distance calculated successfully using metric EPSG:21035 CRS (Rwanda)."
        }

    async def check_intersection(
        self,
        geom1_wkt: Optional[str],
        parcel_upi_1: Optional[str],
        geom2_wkt: Optional[str],
        parcel_upi_2: Optional[str]
    ):
        """
        Determine if two geometries intersect/overlap, and compute the overlapping area and percentages.
        
        Args:
            geom1_wkt: First geometry in WKT format (optional)
            parcel_upi_1: UPI of first parcel - e.g. 1/02/02/03/1390 (optional)
            geom2_wkt: Second geometry in WKT format (optional)
            parcel_upi_2: UPI of second parcel - e.g. 1/02/02/03/1390 (optional)
        """
        geom1 = await self._resolve_geometry(geom1_wkt, parcel_upi_1, "geom1 / parcel_upi_1")
        geom2 = await self._resolve_geometry(geom2_wkt, parcel_upi_2, "geom2 / parcel_upi_2")
        
        # Geometries must be projected to a metric CRS for area calculations
        metric_g1 = to_metric(geom1)
        metric_g2 = to_metric(geom2)
        
        intersects = metric_g1.intersects(metric_g2)
        overlaps = detect_overlap(metric_g1, metric_g2)
        
        intersection_area = calculate_intersection_area(metric_g1, metric_g2)
        
        g1_area = metric_g1.area
        g2_area = metric_g2.area
        
        percentage_g1 = (intersection_area / g1_area * 100.0) if g1_area > 0 else 0.0
        percentage_g2 = (intersection_area / g2_area * 100.0) if g2_area > 0 else 0.0
        
        return {
            "intersects": intersects,
            "overlaps": overlaps,
            "intersection_area_sqm": round(intersection_area, 2),
            "percentage_overlap_geom1": round(percentage_g1, 2),
            "percentage_overlap_geom2": round(percentage_g2, 2)
        }

    async def contains_point(
        self,
        geom_wkt: Optional[str],
        parcel_upi: Optional[str],
        x: float,
        y: float
    ):
        """
        Verify if a geometry or parcel contains or intersects a given latitude/longitude point.
        
        Args:
            geom_wkt: Geometry in WKT format (optional)
            parcel_upi: UPI of parcel - e.g. 1/02/02/03/1390 (optional)
            x: Longitude
            y: Latitude
        """
        geom = await self._resolve_geometry(geom_wkt, parcel_upi, "geom / parcel_upi")
        point_tuple = (x, y)
        
        contains = contains_point(geom, point_tuple)
        intersects = intersects_point(geom, point_tuple)
        
        return {
            "contains": contains,
            "intersects": intersects
        }

    async def check_zoning_overlay(
        self,
        parcel_upi: Optional[str],
        zoning_wkt: str,
        zoning_code: str
    ):
        """
        Overlay a parcel on a zoning district geometry to verify zoning code overlay and compliance area.
        
        Args:
            parcel_upi: UPI of parcel - e.g. 1/02/02/03/1390
            zoning_wkt: Zoning district geometry in WKT format
            zoning_code: Zoning identifier code
        """
        parcel_geom = await self._resolve_geometry(None, parcel_upi, "parcel_upi")
        
        try:
            zoning_geom = wkt.loads(zoning_wkt)
        except Exception as e:
            raise ValueError(f"Invalid WKT format for zoning_wkt: {str(e)}")
            
        # Transform both geometries to metric CRS for accurate compliance calculation
        metric_parcel = to_metric(parcel_geom)
        metric_zoning = to_metric(zoning_geom)
        
        res = overlay_parcel_on_zoning(
            metric_parcel,
            metric_zoning,
            zoning_code
        )
        
        return {
            "intersects": res["intersects"],
            "intersection_area": res["intersection_area"],
            "percentage_overlap": res["percentage_overlap"],
            "zoning_code": res["zoning_code"]
        }