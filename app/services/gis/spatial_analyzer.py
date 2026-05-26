# app/services/gis/spatial_analyzer.py
"""
GIS Spatial Analyzer
Phase 3 — Section 4.1
Land Intelligence System
"""

from typing import List, Tuple, Optional
from shapely.geometry import Point
from shapely import wkb
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union


def calculate_distance(geom1: BaseGeometry, geom2: BaseGeometry) -> float:
    """
    Calculate minimum distance between two geometries.
    
    IMPORTANT: Distance units depend on the geometry's Coordinate Reference System (CRS).
    If geometries are in WGS84 (latitude/longitude), result is in degrees, not meters.
    For accurate meter-based distances, ensure geometries are projected to a metric CRS
    (e.g., UTM zone) before calling this function.
    
    Args:
        geom1: First geometry
        geom2: Second geometry
        
    Returns:
        Minimum distance in CRS units (degrees if WGS84, meters if projected)
    """
    if geom1.is_empty or geom2.is_empty:
        return -1.0
    
    return geom1.distance(geom2)


def calculate_distance_from_wkb(wkb1: bytes, wkb2: bytes) -> float:
    """
    Calculate minimum distance between two geometries from WKB bytes.
    
    IMPORTANT: Distance units depend on the geometry's Coordinate Reference System (CRS).
    If geometries are in WGS84 (latitude/longitude), result is in degrees, not meters.
    For accurate meter-based distances, ensure geometries are projected to a metric CRS
    (e.g., UTM zone) before calling this function.
    
    Args:
        wkb1: First geometry in WKB bytes
        wkb2: Second geometry in WKB bytes
        
    Returns:
        Minimum distance in CRS units (degrees if WGS84, meters if projected)
    """
    geom1 = wkb.loads(wkb1)
    geom2 = wkb.loads(wkb2)
    return calculate_distance(geom1, geom2)


def contains_point(geom: BaseGeometry, point: Tuple[float, float]) -> bool:
    """
    Check if geometry contains a point.
    
    Note: Contains returns False if point is exactly on the boundary.
    For boundary-inclusive checks, use intersects_point instead.
    
    Args:
        geom: Geometry to check
        point: (longitude, latitude) tuple
        
    Returns:
        True if geometry contains point, False otherwise
    """
    if geom.is_empty:
        return False
    
    pt = Point(point)
    return geom.contains(pt)


def contains_point_from_wkb(wkb_bytes: bytes, point: Tuple[float, float]) -> bool:
    """
    Check if geometry contains a point from WKB bytes.
    
    Note: Contains returns False if point is exactly on the boundary.
    For boundary-inclusive checks, use intersects_point_from_wkb instead.
    
    Args:
        wkb_bytes: Geometry in WKB bytes
        point: (longitude, latitude) tuple
        
    Returns:
        True if geometry contains point, False otherwise
    """
    geom = wkb.loads(wkb_bytes)
    return contains_point(geom, point)


def intersects_point(geom: BaseGeometry, point: Tuple[float, float]) -> bool:
    """
    Check if geometry intersects a point (including boundary).
    
    Args:
        geom: Geometry to check
        point: (longitude, latitude) tuple
        
    Returns:
        True if geometry intersects point, False otherwise
    """
    if geom.is_empty:
        return False
    
    pt = Point(point)
    return geom.intersects(pt)


def intersects_point_from_wkb(wkb_bytes: bytes, point: Tuple[float, float]) -> bool:
    """
    Check if geometry intersects a point from WKB bytes (including boundary).
    
    Args:
        wkb_bytes: Geometry in WKB bytes
        point: (longitude, latitude) tuple
        
    Returns:
        True if geometry intersects point, False otherwise
    """
    geom = wkb.loads(wkb_bytes)
    return intersects_point(geom, point)


def touches(geom1: BaseGeometry, geom2: BaseGeometry) -> bool:
    """
    Check if two geometries touch (share boundary but do not overlap).
    
    Args:
        geom1: First geometry
        geom2: Second geometry
        
    Returns:
        True if geometries touch, False otherwise
    """
    if geom1.is_empty or geom2.is_empty:
        return False
    
    return geom1.touches(geom2)


def touches_from_wkb(wkb1: bytes, wkb2: bytes) -> bool:
    """
    Check if two geometries touch from WKB bytes.
    
    Args:
        wkb1: First geometry in WKB bytes
        wkb2: Second geometry in WKB bytes
        
    Returns:
        True if geometries touch, False otherwise
    """
    geom1 = wkb.loads(wkb1)
    geom2 = wkb.loads(wkb2)
    return touches(geom1, geom2)


def is_within(geom1: BaseGeometry, geom2: BaseGeometry) -> bool:
    """
    Check if geom1 is completely within geom2.
    
    Args:
        geom1: Inner geometry
        geom2: Outer geometry
        
    Returns:
        True if geom1 is within geom2, False otherwise
    """
    if geom1.is_empty or geom2.is_empty:
        return False
    
    return geom1.within(geom2)


def is_within_from_wkb(wkb1: bytes, wkb2: bytes) -> bool:
    """
    Check if geom1 is completely within geom2 from WKB bytes.
    
    Args:
        wkb1: Inner geometry in WKB bytes
        wkb2: Outer geometry in WKB bytes
        
    Returns:
        True if geom1 is within geom2, False otherwise
    """
    geom1 = wkb.loads(wkb1)
    geom2 = wkb.loads(wkb2)
    return is_within(geom1, geom2)


def get_centroid(geom: BaseGeometry) -> Tuple[float, float]:
    """
    Get centroid of geometry.
    
    WARNING: For concave or irregular shapes (C-shaped, L-shaped), the centroid
    may fall outside the geometry boundary. For guaranteed inside-point suitable
    for label placement, use get_point_on_surface() instead.
    
    Args:
        geom: Geometry
        
    Returns:
        (longitude, latitude) tuple of centroid
    """
    if geom.is_empty:
        return (0.0, 0.0)
    
    centroid = geom.centroid
    return (centroid.x, centroid.y)


def get_centroid_from_wkb(wkb_bytes: bytes) -> Tuple[float, float]:
    """
    Get centroid of geometry from WKB bytes.
    
    WARNING: For concave or irregular shapes, the centroid may fall outside
    the geometry boundary. Use get_point_on_surface_from_wkb for label placement.
    
    Args:
        wkb_bytes: Geometry in WKB bytes
        
    Returns:
        (longitude, latitude) tuple of centroid
    """
    geom = wkb.loads(wkb_bytes)
    return get_centroid(geom)


def get_point_on_surface(geom: BaseGeometry) -> Tuple[float, float]:
    """
    Get a point guaranteed to be inside the geometry surface.
    
    This is ideal for label placement on irregularly shaped parcels
    where centroid may fall outside the boundary.
    
    Args:
        geom: Geometry
        
    Returns:
        (longitude, latitude) tuple of interior point
    """
    if geom.is_empty:
        return (0.0, 0.0)
    
    point = geom.representative_point()
    return (point.x, point.y)


def get_point_on_surface_from_wkb(wkb_bytes: bytes) -> Tuple[float, float]:
    """
    Get a point guaranteed to be inside the geometry surface from WKB bytes.
    
    This is ideal for label placement on irregularly shaped parcels.
    
    Args:
        wkb_bytes: Geometry in WKB bytes
        
    Returns:
        (longitude, latitude) tuple of interior point
    """
    geom = wkb.loads(wkb_bytes)
    return get_point_on_surface(geom)


def get_bounds(geom: BaseGeometry) -> Tuple[float, float, float, float]:
    """
    Get bounding box of geometry.
    
    Returns:
        (min_x, min_y, max_x, max_y) tuple suitable for map fitBounds()
    """
    if geom.is_empty:
        return (0.0, 0.0, 0.0, 0.0)
    
    bounds = geom.bounds
    return (bounds[0], bounds[1], bounds[2], bounds[3])


def get_bounds_from_wkb(wkb_bytes: bytes) -> Tuple[float, float, float, float]:
    """
    Get bounding box of geometry from WKB bytes.
    
    Returns:
        (min_x, min_y, max_x, max_y) tuple suitable for map fitBounds()
    """
    geom = wkb.loads(wkb_bytes)
    return get_bounds(geom)


def calculate_total_area(geometries: List[BaseGeometry]) -> float:
    """
    Calculate total area of multiple geometries.
    
    Note: This function unions overlapping geometries first to ensure
    overlapping areas are not counted twice. The result represents the
    unique physical footprint area.
    
    Args:
        geometries: List of geometries
        
    Returns:
        Total area in square meters
    """
    if not geometries:
        return 0.0
    
    valid_geoms = [g for g in geometries if not g.is_empty]
    if not valid_geoms:
        return 0.0
    
    # Union to avoid double-counting overlapping areas
    union = unary_union(valid_geoms)
    return union.area


def union_geometries(geometries: List[BaseGeometry]) -> Optional[BaseGeometry]:
    """
    Union multiple geometries into one.
    
    Args:
        geometries: List of geometries
        
    Returns:
        Union geometry, or None if empty list
    """
    if not geometries:
        return None
    
    valid_geoms = [g for g in geometries if not g.is_empty]
    if not valid_geoms:
        return None
    
    return unary_union(valid_geoms)