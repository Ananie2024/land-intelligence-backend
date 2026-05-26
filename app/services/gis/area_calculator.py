# app/services/gis/area_calculator.py
"""
GIS Area Calculator
Phase 3 — Section 4.1
Land Intelligence System
"""

from typing import List, Tuple
from shapely.geometry import Polygon
from shapely import wkb
from shapely.geometry.base import BaseGeometry


def calculate_area_from_wkb(wkb_bytes: bytes) -> float:
    """
    Calculate area from WKB bytes.
    
    Args:
        wkb_bytes: WKB geometry in bytes
        
    Returns:
        Area in square meters
    """
    geom = wkb.loads(wkb_bytes)
    return calculate_area_from_geometry(geom)


def calculate_area_from_coordinates(coordinates: List[Tuple[float, float]]) -> float:
    """
    Calculate area from coordinate tuples.
    
    Args:
        coordinates: List of (longitude, latitude) points
        
    Returns:
        Area in square meters
    """
    if len(coordinates) < 3:
        raise ValueError("At least 3 points required to form a polygon")
    
    polygon = Polygon(coordinates)
    
    # Ensure polygon is valid
    if not polygon.is_valid:
        polygon = polygon.buffer(0)
    
    return calculate_area_from_geometry(polygon)


def calculate_area_from_geometry(geometry: BaseGeometry) -> float:
    """
    Calculate area from shapely geometry.
    
    Args:
        geometry: Shapely geometry object (Polygon, MultiPolygon)
        
    Returns:
        Area in square meters
    """
    if geometry.is_empty:
        return 0.0
    
    if geometry.geom_type == 'Polygon':
        return geometry.area
    elif geometry.geom_type == 'MultiPolygon':
        return geometry.area
    else:
        return 0.0