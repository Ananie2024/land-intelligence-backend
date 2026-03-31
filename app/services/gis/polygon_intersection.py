"""
GIS Polygon Intersection
Phase 3 — Section 4.1
Land Intelligence System
"""

from typing import Optional
from shapely.geometry import Polygon, MultiPolygon
from shapely import wkb
from shapely.geometry.base import BaseGeometry


def detect_overlap(geom1: BaseGeometry, geom2: BaseGeometry) -> bool:
    """
    Detect if two geometries overlap.
    
    Args:
        geom1: First geometry
        geom2: Second geometry
        
    Returns:
        True if geometries overlap, False otherwise
    """
    if not geom1.intersects(geom2):
        return False
    
    if geom1.is_empty or geom2.is_empty:
        return False
    
    return geom1.intersects(geom2) and not geom1.touches(geom2)


def calculate_intersection_area(geom1: BaseGeometry, geom2: BaseGeometry) -> float:
    """
    Calculate intersection area between two geometries.
    
    Args:
        geom1: First geometry
        geom2: Second geometry
        
    Returns:
        Intersection area in square meters
    """
    if geom1.is_empty or geom2.is_empty:
        return 0.0
    
    intersection = geom1.intersection(geom2)
    if intersection.is_empty:
        return 0.0
    
    return intersection.area


def calculate_intersection_area_from_wkb(wkb1: bytes, wkb2: bytes) -> float:
    """
    Calculate intersection area between two geometries from WKB bytes.
    
    Args:
        wkb1: First geometry in WKB bytes
        wkb2: Second geometry in WKB bytes
        
    Returns:
        Intersection area in square meters
    """
    geom1 = wkb.loads(wkb1)
    geom2 = wkb.loads(wkb2)
    return calculate_intersection_area(geom1, geom2)


def detect_overlap_from_wkb(wkb1: bytes, wkb2: bytes) -> bool:
    """
    Detect overlap between two geometries from WKB bytes.
    
    Args:
        wkb1: First geometry in WKB bytes
        wkb2: Second geometry in WKB bytes
        
    Returns:
        True if geometries overlap, False otherwise
    """
    geom1 = wkb.loads(wkb1)
    geom2 = wkb.loads(wkb2)
    return detect_overlap(geom1, geom2)


def get_intersection_geometry(geom1: BaseGeometry, geom2: BaseGeometry) -> Optional[BaseGeometry]:
    """
    Get intersection geometry between two geometries.
    
    Args:
        geom1: First geometry
        geom2: Second geometry
        
    Returns:
        Intersection geometry, or None if no intersection
    """
    if geom1.is_empty or geom2.is_empty:
        return None
    
    intersection = geom1.intersection(geom2)
    if intersection.is_empty:
        return None
    
    return intersection


def get_intersection_geometry_from_wkb(wkb1: bytes, wkb2: bytes) -> Optional[BaseGeometry]:
    """
    Get intersection geometry between two geometries from WKB bytes.
    
    Args:
        wkb1: First geometry in WKB bytes
        wkb2: Second geometry in WKB bytes
        
    Returns:
        Intersection geometry, or None if no intersection
    """
    geom1 = wkb.loads(wkb1)
    geom2 = wkb.loads(wkb2)
    return get_intersection_geometry(geom1, geom2)# app/services/gis/polygon_intersection.py
