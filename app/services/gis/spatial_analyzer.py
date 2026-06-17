# app/services/gis/spatial_analyzer.py
"""
GIS Spatial Analyzer
Phase 3 — Section 4.1
Land Intelligence System
"""

from typing import List, Tuple, Optional, Any
from shapely.geometry import Point
from shapely import wkb
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
import binascii


def ensure_geometry(data: Any) -> BaseGeometry:
    """
    Convert various spatial data formats to a Shapely geometry.
    
    Supports:
    - Shapely BaseGeometry (returns as is)
    - WKB bytes
    - WKB hex string
    - GeoAlchemy2 WKBElement
    
    Args:
        data: Spatial data in any supported format
        
    Returns:
        Shapely geometry
    """
    if data is None:
        return Point()
    
    if isinstance(data, BaseGeometry):
        return data
        
    # Handle GeoAlchemy2 WKBElement
    if hasattr(data, "data"):
        data = data.data
        
    if isinstance(data, bytes):
        try:
            return wkb.loads(data)
        except Exception:
            # Try hex decoding if it's actually hex-encoded bytes
            try:
                return wkb.loads(binascii.unhexlify(data))
            except Exception:
                raise ValueError("Could not load geometry from bytes")
                
    if isinstance(data, str):
        try:
            return wkb.loads(binascii.unhexlify(data))
        except Exception:
            raise ValueError("Could not load geometry from hex string")
            
    raise TypeError(f"Unsupported geometry data type: {type(data)}")


def calculate_distance(geom1: Any, geom2: Any) -> float:
    """
    Calculate minimum distance between two geometries in meters.
    
    Args:
        geom1: First geometry (Shapely, WKB, or WKBElement)
        geom2: Second geometry (Shapely, WKB, or WKBElement)
        
    Returns:
        Minimum distance in meters
    """
    g1 = ensure_geometry(geom1)
    g2 = ensure_geometry(geom2)
    
    if g1.is_empty or g2.is_empty:
        return -1.0
    
    # Transform to metric CRS
    m1 = to_metric(g1)
    m2 = to_metric(g2)
    
    return m1.distance(m2)


def calculate_distance_from_wkb(wkb1: Any, wkb2: Any) -> float:
    """
    Calculate minimum distance between two geometries from WKB.
    """
    return calculate_distance(wkb1, wkb2)


def contains_point(geom: Any, point: Tuple[float, float]) -> bool:
    """
    Check if geometry contains a point.
    """
    g = ensure_geometry(geom)
    if g.is_empty:
        return False
    
    pt = Point(point)
    return g.contains(pt)


def contains_point_from_wkb(wkb_data: Any, point: Tuple[float, float]) -> bool:
    """
    Check if geometry contains a point from WKB.
    """
    return contains_point(wkb_data, point)


def intersects_point(geom: Any, point: Tuple[float, float]) -> bool:
    """
    Check if geometry intersects a point (including boundary).
    """
    g = ensure_geometry(geom)
    if g.is_empty:
        return False
    
    pt = Point(point)
    return g.intersects(pt)


def intersects_point_from_wkb(wkb_data: Any, point: Tuple[float, float]) -> bool:
    """
    Check if geometry intersects a point from WKB.
    """
    return intersects_point(wkb_data, point)


def touches(geom1: Any, geom2: Any) -> bool:
    """
    Check if two geometries touch.
    """
    g1 = ensure_geometry(geom1)
    g2 = ensure_geometry(geom2)
    
    if g1.is_empty or g2.is_empty:
        return False
    
    return g1.touches(g2)


def touches_from_wkb(wkb1: Any, wkb2: Any) -> bool:
    """
    Check if two geometries touch from WKB.
    """
    return touches(wkb1, wkb2)


def is_within(geom1: Any, geom2: Any) -> bool:
    """
    Check if geom1 is completely within geom2.
    """
    g1 = ensure_geometry(geom1)
    g2 = ensure_geometry(geom2)
    
    if g1.is_empty or g2.is_empty:
        return False
    
    return g1.within(g2)


def is_within_from_wkb(wkb1: Any, wkb2: Any) -> bool:
    """
    Check if geom1 is completely within geom2 from WKB.
    """
    return is_within(wkb1, wkb2)


def get_centroid(geom: Any) -> Tuple[float, float]:
    """
    Get centroid of geometry.
    """
    g = ensure_geometry(geom)
    if g.is_empty:
        return (0.0, 0.0)
    
    centroid = g.centroid
    return (centroid.x, centroid.y)


def get_centroid_from_wkb(wkb_data: Any) -> Tuple[float, float]:
    """
    Get centroid of geometry from WKB.
    """
    return get_centroid(wkb_data)


def get_point_on_surface(geom: Any) -> Tuple[float, float]:
    """
    Get a point guaranteed to be inside the geometry surface.
    """
    g = ensure_geometry(geom)
    if g.is_empty:
        return (0.0, 0.0)
    
    point = g.representative_point()
    return (point.x, point.y)


def get_point_on_surface_from_wkb(wkb_data: Any) -> Tuple[float, float]:
    """
    Get a point guaranteed to be inside the geometry surface from WKB.
    """
    return get_point_on_surface(wkb_data)


def get_bounds(geom: Any) -> Tuple[float, float, float, float]:
    """
    Get bounding box of geometry.
    """
    g = ensure_geometry(geom)
    if g.is_empty:
        return (0.0, 0.0, 0.0, 0.0)
    
    bounds = g.bounds
    return (bounds[0], bounds[1], bounds[2], bounds[3])


def get_bounds_from_wkb(wkb_data: Any) -> Tuple[float, float, float, float]:
    """
    Get bounding box of geometry from WKB.
    """
    return get_bounds(wkb_data)


from app.utils.coordinate_transformations import to_metric


def calculate_total_area(geometries: List[Any]) -> float:
    """
    Calculate total area of multiple geometries in square meters.
    """
    if not geometries:
        return 0.0
    
    valid_geoms = [ensure_geometry(g) for g in geometries if g is not None]
    valid_geoms = [g for g in valid_geoms if not g.is_empty]
    
    if not valid_geoms:
        return 0.0
    
    # Union to avoid double-counting overlapping areas
    union = unary_union(valid_geoms)
    
    # Transform to metric CRS for accurate area calculation
    metric_union = to_metric(union)
    
    return metric_union.area


def union_geometries(geometries: List[Any]) -> Optional[BaseGeometry]:
    """
    Union multiple geometries into one.
    """
    if not geometries:
        return None
    
    valid_geoms = [ensure_geometry(g) for g in geometries if g is not None]
    valid_geoms = [g for g in valid_geoms if not g.is_empty]
    
    if not valid_geoms:
        return None
    
    return unary_union(valid_geoms)