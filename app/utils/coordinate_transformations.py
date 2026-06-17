"""
Coordinate Transformation Utilities
Phase 3 — Section 4.1
Land Intelligence System
"""

from typing import Tuple
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform
import pyproj

# Default WGS84 (GPS) CRS
WGS84_CRS = "EPSG:4326"

# Rwanda-specific metric CRS (Arc 1960 / UTM zone 35S)
# This is a metric CRS suitable for area calculations in Rwanda
RWANDA_METRIC_CRS = "EPSG:21035"


def get_transformer(from_crs: str, to_crs: str) -> pyproj.Transformer:
    """
    Get a pyproj transformer between two CRS.
    
    Args:
        from_crs: Source CRS (e.g., "EPSG:4326")
        to_crs: Destination CRS (e.g., "EPSG:21035")
        
    Returns:
        Transformer object
    """
    return pyproj.Transformer.from_crs(from_crs, to_crs, always_xy=True)


def transform_geometry(geometry: BaseGeometry, from_crs: str = WGS84_CRS, to_crs: str = RWANDA_METRIC_CRS) -> BaseGeometry:
    """
    Transform a geometry from one CRS to another.
    
    Args:
        geometry: Shapely geometry to transform
        from_crs: Source CRS
        to_crs: Destination CRS
        
    Returns:
        Transformed shapely geometry
    """
    if geometry.is_empty:
        return geometry
    
    project = get_transformer(from_crs, to_crs).transform
    return transform(project, geometry)


def to_metric(geometry: BaseGeometry) -> BaseGeometry:
    """
    Transform a WGS84 geometry to a metric CRS (Rwanda UTM).
    
    Args:
        geometry: Geometry in WGS84 (EPSG:4326)
        
    Returns:
        Geometry in metric units (meters)
    """
    return transform_geometry(geometry, WGS84_CRS, RWANDA_METRIC_CRS)


def from_metric(geometry: BaseGeometry) -> BaseGeometry:
    """
    Transform a metric geometry back to WGS84.
    
    Args:
        geometry: Geometry in metric units (meters)
        
    Returns:
        Geometry in WGS84 (EPSG:4326)
    """
    return transform_geometry(geometry, RWANDA_METRIC_CRS, WGS84_CRS)
