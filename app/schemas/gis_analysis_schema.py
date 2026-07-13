# app/schemas/gis_analysis_schema.py
"""
GIS Analysis Schemas
Phase 3 — Section 3.2
Land Intelligence System
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class DistanceRequest(BaseModel):
    """
    Schema for calculating distance between two geometries or two parcels.
    """
    geom1_wkt: Optional[str] = Field(None, description="First geometry in Well-Known Text (WKT) format")
    geom2_wkt: Optional[str] = Field(None, description="Second geometry in Well-Known Text (WKT) format")
    parcel_upi_1: Optional[str] = Field(None, description="UPI of first parcel (alternative to geom1_wkt) - e.g. 1/02/02/03/1390")
    parcel_upi_2: Optional[str] = Field(None, description="UPI of second parcel (alternative to geom2_wkt) - e.g. 1/02/02/03/1390")


class DistanceResponse(BaseModel):
    """
    Response schema for distance calculation.
    """
    distance_meters: float = Field(..., description="Minimum distance in meters (returns -1.0 if invalid/empty)")
    message: str = Field(..., description="Details or status message")


class IntersectionRequest(BaseModel):
    """
    Schema for detecting overlap and intersection between two geometries/parcels.
    """
    geom1_wkt: Optional[str] = Field(None, description="First geometry in Well-Known Text (WKT)")
    geom2_wkt: Optional[str] = Field(None, description="Second geometry in Well-Known Text (WKT)")
    parcel_upi_1: Optional[str] = Field(None, description="UPI of first parcel - e.g. 1/02/02/03/1390")
    parcel_upi_2: Optional[str] = Field(None, description="UPI of second parcel - e.g. 1/02/02/03/1390")


class IntersectionResponse(BaseModel):
    """
    Response schema for overlap/intersection detection.
    """
    intersects: bool = Field(..., description="Whether the geometries intersect")
    overlaps: bool = Field(..., description="Whether the geometries overlap (intersects and doesn't just touch)")
    intersection_area_sqm: float = Field(..., description="Intersection area in square meters")
    percentage_overlap_geom1: float = Field(..., description="Percentage of geom1's area that overlaps with geom2")
    percentage_overlap_geom2: float = Field(..., description="Percentage of geom2's area that overlaps with geom1")


class ContainsPointRequest(BaseModel):
    """
    Schema to check if a geometry/parcel contains a point.
    """
    geom_wkt: Optional[str] = Field(None, description="Geometry in Well-Known Text (WKT)")
    parcel_upi: Optional[str] = Field(None, description="Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390")
    x: float = Field(..., description="Longitude / X coordinate")
    y: float = Field(..., description="Latitude / Y coordinate")


class ContainsPointResponse(BaseModel):
    """
    Response schema for point containment.
    """
    contains: bool = Field(..., description="True if geometry contains the point")
    intersects: bool = Field(..., description="True if geometry intersects/touches the point")


class OverlayRequest(BaseModel):
    """
    Schema for overlaying a parcel on a zoning geometry.
    """
    parcel_upi: str = Field(..., description="Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390")
    zoning_wkt: str = Field(..., description="Zoning district geometry in WKT")
    zoning_code: str = Field(..., description="Zoning identifier code")


class OverlayResponse(BaseModel):
    """
    Response schema for parcel-to-zoning overlay.
    """
    intersects: bool = Field(..., description="True if parcel intersects the zoning district")
    intersection_area: float = Field(..., description="Intersection area in square meters")
    percentage_overlap: float = Field(..., description="Percentage of parcel overlapping the zoning district")
    zoning_code: str = Field(..., description="Zoning identifier code")