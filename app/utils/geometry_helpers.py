# app/utils/geometry_helpers.py
"""
Geometry Helpers Utility
Provides utility functions for working with spatial geometries, converting formats,
and extracting coordinates.
"""

import binascii
from typing import Dict, Any, Tuple, Optional
from shapely import wkt, wkb
from shapely.geometry import shape, mapping, Polygon, box
from shapely.geometry.base import BaseGeometry

def wkb_hex_to_wkt(wkb_hex: str) -> str:
    """
    Convert a WKB (Well-Known Binary) hex string to a WKT (Well-Known Text) string.
    
    Args:
        wkb_hex: The hexadecimal string representation of WKB.
        
    Returns:
        The WKT string.
    """
    if not wkb_hex:
        return ""
    try:
        geom = wkb.loads(binascii.unhexlify(wkb_hex))
        return geom.wkt
    except Exception as e:
        raise ValueError(f"Failed to parse WKB hex string: {str(e)}")

def wkt_to_wkb_hex(wkt_str: str) -> str:
    """
    Convert a WKT string to a WKB hex string.
    
    Args:
        wkt_str: The WKT representation of geometry.
        
    Returns:
        Hexadecimal WKB string.
    """
    if not wkt_str:
        return ""
    try:
        geom = wkt.loads(wkt_str)
        return binascii.hexlify(wkb.dumps(geom)).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Failed to parse WKT string: {str(e)}")

def geojson_to_geometry(geojson_dict: Dict[str, Any]) -> BaseGeometry:
    """
    Convert a GeoJSON geometry dictionary to a Shapely geometry object.
    
    Args:
        geojson_dict: GeoJSON geometry structure.
        
    Returns:
        Shapely geometry.
    """
    try:
        return shape(geojson_dict)
    except Exception as e:
        raise ValueError(f"Failed to convert GeoJSON to geometry: {str(e)}")

def geometry_to_geojson(geom: BaseGeometry) -> Dict[str, Any]:
    """
    Convert a Shapely geometry to a GeoJSON geometry dictionary.
    
    Args:
        geom: A Shapely geometry.
        
    Returns:
        GeoJSON geometry dict.
    """
    if geom.is_empty:
        return {}
    return mapping(geom)

def create_bbox_polygon(min_x: float, min_y: float, max_x: float, max_y: float) -> Polygon:
    """
    Create a Shapely Polygon from bounding box limits.
    """
    return box(min_x, min_y, max_x, max_y)

def ensure_wkb_hex(data: Any) -> Optional[str]:
    """
    Convert geometry representation to WKB hex string if not already.
    
    Args:
        data: Shapely BaseGeometry, WKB bytes, or WKB hex.
        
    Returns:
        Hex-encoded WKB string.
    """
    if data is None:
        return None
    if isinstance(data, str):
        # Already a hex string?
        try:
            binascii.unhexlify(data)
            return data
        except Exception:
            # Maybe WKT?
            return wkt_to_wkb_hex(data)
    if isinstance(data, bytes):
        return binascii.hexlify(data).decode("utf-8")
    if isinstance(data, BaseGeometry):
        return binascii.hexlify(wkb.dumps(data)).decode("utf-8")
        
    # Check for GeoAlchemy WKBElement
    if hasattr(data, "data"):
        wkb_bytes = data.data
        if isinstance(wkb_bytes, bytes):
            return binascii.hexlify(wkb_bytes).decode("utf-8")
        elif isinstance(wkb_bytes, str):
            return wkb_bytes
            
    raise TypeError(f"Unsupported geometry data type for WKB conversion: {type(data)}")
