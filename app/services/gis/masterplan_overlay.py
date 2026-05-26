# app/services/gis/masterplan_overlay.py
"""
GIS Masterplan Overlay
Phase 3 — Section 4.1
Land Intelligence System
"""

from typing import List, Tuple, Optional, Dict, Any
from shapely import wkb
from shapely.geometry.base import BaseGeometry

# Minimum overlap percentage to consider a valid zoning intersection
# This filters out "sliver polygons" caused by digital mapping errors
MIN_VALID_OVERLAP_PERCENT = 1.0


def overlay_parcel_on_zoning(
    parcel_geom: BaseGeometry,
    zoning_geom: BaseGeometry,
    zoning_code: str
) -> Dict[str, Any]:
    """
    Overlay a single parcel on a zoning layer and return intersection details.
    
    IMPORTANT: Area calculations require a projected Coordinate Reference System.
    Ensure both geometries use the same CRS (e.g., UTM, EPSG:3857) for accurate
    area measurements. WGS84 (latitude/longitude) will produce degrees, not meters.
    
    Args:
        parcel_geom: Parcel geometry
        zoning_geom: Zoning district geometry
        zoning_code: Zoning code identifier
        
    Returns:
        Dictionary with overlay results
    """
    if parcel_geom.is_empty or zoning_geom.is_empty:
        return {
            "intersects": False,
            "intersection_area": 0.0,
            "percentage_overlap": 0.0,
            "zoning_code": zoning_code
        }
    
    intersects = parcel_geom.intersects(zoning_geom)
    
    if not intersects:
        return {
            "intersects": False,
            "intersection_area": 0.0,
            "percentage_overlap": 0.0,
            "zoning_code": zoning_code
        }
    
    intersection = parcel_geom.intersection(zoning_geom)
    intersection_area = intersection.area
    
    if parcel_geom.area > 0:
        percentage = (intersection_area / parcel_geom.area) * 100
    else:
        percentage = 0.0
    
    return {
        "intersects": True,
        "intersection_area": round(intersection_area, 2),
        "percentage_overlap": round(percentage, 2),
        "zoning_code": zoning_code
    }


def overlay_parcel_on_zoning_from_wkb(
    parcel_wkb: bytes,
    zoning_wkb: bytes,
    zoning_code: str
) -> Dict[str, Any]:
    """
    Overlay a single parcel on a zoning layer from WKB bytes.
    
    IMPORTANT: Area calculations require a projected Coordinate Reference System.
    Ensure both geometries use the same CRS.
    
    Args:
        parcel_wkb: Parcel geometry in WKB bytes
        zoning_wkb: Zoning district geometry in WKB bytes
        zoning_code: Zoning code identifier
        
    Returns:
        Dictionary with overlay results
    """
    parcel_geom = wkb.loads(parcel_wkb)
    zoning_geom = wkb.loads(zoning_wkb)
    return overlay_parcel_on_zoning(parcel_geom, zoning_geom, zoning_code)


def find_zoning_district(
    parcel_geom: BaseGeometry,
    zoning_layers: List[Tuple[BaseGeometry, str]],
    min_overlap_percent: float = MIN_VALID_OVERLAP_PERCENT
) -> Optional[Dict[str, Any]]:
    """
    Find which zoning district a parcel falls into.
    
    Returns the zoning district with the highest valid overlap.
    Overlaps below min_overlap_percent are filtered out as sliver polygons.
    
    Args:
        parcel_geom: Parcel geometry
        zoning_layers: List of (geometry, zoning_code) tuples
        min_overlap_percent: Minimum overlap percentage to consider valid
        
    Returns:
        Zoning district info if found, None otherwise
    """
    if parcel_geom.is_empty or not zoning_layers:
        return None
    
    best_match = None
    max_overlap = 0.0
    
    for zoning_geom, zoning_code in zoning_layers:
        if zoning_geom.is_empty:
            continue
        
        if parcel_geom.intersects(zoning_geom):
            intersection = parcel_geom.intersection(zoning_geom)
            overlap_area = intersection.area
            
            if parcel_geom.area > 0:
                percentage = (overlap_area / parcel_geom.area) * 100
            else:
                percentage = 0.0
            
            # Filter out sliver polygons below threshold
            if percentage < min_overlap_percent:
                continue
            
            if percentage > max_overlap:
                max_overlap = percentage
                best_match = {
                    "zoning_code": zoning_code,
                    "overlap_area": round(overlap_area, 2),
                    "percentage_overlap": round(percentage, 2)
                }
    
    return best_match


def find_zoning_district_from_wkb(
    parcel_wkb: bytes,
    zoning_layers: List[Tuple[bytes, str]],
    min_overlap_percent: float = MIN_VALID_OVERLAP_PERCENT
) -> Optional[Dict[str, Any]]:
    """
    Find which zoning district a parcel falls into from WKB bytes.
    
    Args:
        parcel_wkb: Parcel geometry in WKB bytes
        zoning_layers: List of (wkb_bytes, zoning_code) tuples
        min_overlap_percent: Minimum overlap percentage to consider valid
        
    Returns:
        Zoning district info if found, None otherwise
    """
    parcel_geom = wkb.loads(parcel_wkb)
    
    zoning_geoms = []
    for zoning_wkb, zoning_code in zoning_layers:
        zoning_geom = wkb.loads(zoning_wkb)
        zoning_geoms.append((zoning_geom, zoning_code))
    
    return find_zoning_district(parcel_geom, zoning_geoms, min_overlap_percent)


def get_zoning_compliance(
    parcel_geom: BaseGeometry,
    allowed_zones: List[str],
    zoning_layers: List[Tuple[BaseGeometry, str]],
    min_overlap_percent: float = MIN_VALID_OVERLAP_PERCENT
) -> Dict[str, Any]:
    """
    Check if a parcel is compliant with allowed zoning categories.
    
    For split-zoned parcels, compliance is determined by the primary zoning
    district (the one with the highest valid overlap).
    
    Args:
        parcel_geom: Parcel geometry
        allowed_zones: List of allowed zoning codes
        zoning_layers: List of (geometry, zoning_code) tuples
        min_overlap_percent: Minimum overlap percentage to consider valid
        
    Returns:
        Compliance status with details
    """
    if parcel_geom.is_empty:
        return {
            "compliant": False,
            "message": "Empty parcel geometry",
            "zoning_found": None,
            "allowed_zones": allowed_zones
        }
    
    zoning_info = find_zoning_district(parcel_geom, zoning_layers, min_overlap_percent)
    
    if zoning_info is None:
        return {
            "compliant": False,
            "message": "Parcel does not fall within any zoning district",
            "zoning_found": None,
            "allowed_zones": allowed_zones
        }
    
    is_compliant = zoning_info["zoning_code"] in allowed_zones
    
    return {
        "compliant": is_compliant,
        "message": "Parcel is compliant" if is_compliant else f"Parcel zoning '{zoning_info['zoning_code']}' not in allowed zones",
        "zoning_found": zoning_info,
        "allowed_zones": allowed_zones
    }


def get_zoning_compliance_from_wkb(
    parcel_wkb: bytes,
    allowed_zones: List[str],
    zoning_layers: List[Tuple[bytes, str]],
    min_overlap_percent: float = MIN_VALID_OVERLAP_PERCENT
) -> Dict[str, Any]:
    """
    Check if a parcel is compliant with allowed zoning categories from WKB bytes.
    
    Args:
        parcel_wkb: Parcel geometry in WKB bytes
        allowed_zones: List of allowed zoning codes
        zoning_layers: List of (wkb_bytes, zoning_code) tuples
        min_overlap_percent: Minimum overlap percentage to consider valid
        
    Returns:
        Compliance status with details
    """
    parcel_geom = wkb.loads(parcel_wkb)
    
    zoning_geoms = []
    for zoning_wkb, zoning_code in zoning_layers:
        zoning_geom = wkb.loads(zoning_wkb)
        zoning_geoms.append((zoning_geom, zoning_code))
    
    return get_zoning_compliance(parcel_geom, allowed_zones, zoning_geoms, min_overlap_percent)


def calculate_zoning_coverage(
    parcel_geom: BaseGeometry,
    zoning_layers: List[Tuple[BaseGeometry, str]],
    min_overlap_percent: float = MIN_VALID_OVERLAP_PERCENT
) -> List[Dict[str, Any]]:
    """
    Calculate coverage of parcel across multiple zoning districts.
    
    Filters out sliver polygons (overlaps below min_overlap_percent)
    to avoid reporting false split-zoning due to digitization errors.
    
    IMPORTANT: Area calculations require a projected Coordinate Reference System.
    Ensure all geometries use the same CRS (e.g., UTM, EPSG:3857) for accurate
    area measurements.
    
    Args:
        parcel_geom: Parcel geometry
        zoning_layers: List of (geometry, zoning_code) tuples
        min_overlap_percent: Minimum overlap percentage to consider valid
        
    Returns:
        List of zoning districts with coverage percentages (filtered and sorted)
    """
    if parcel_geom.is_empty or not zoning_layers:
        return []
    
    results = []
    
    for zoning_geom, zoning_code in zoning_layers:
        if zoning_geom.is_empty:
            continue
        
        if parcel_geom.intersects(zoning_geom):
            intersection = parcel_geom.intersection(zoning_geom)
            intersection_area = intersection.area
            
            if parcel_geom.area > 0:
                percentage = (intersection_area / parcel_geom.area) * 100
            else:
                percentage = 0.0
            
            # Filter out sliver polygons below threshold
            if percentage >= min_overlap_percent:
                results.append({
                    "zoning_code": zoning_code,
                    "intersection_area": round(intersection_area, 2),
                    "percentage_coverage": round(percentage, 2)
                })
    
    # Sort by coverage percentage descending
    results.sort(key=lambda x: x["percentage_coverage"], reverse=True)
    
    return results


def calculate_zoning_coverage_from_wkb(
    parcel_wkb: bytes,
    zoning_layers: List[Tuple[bytes, str]],
    min_overlap_percent: float = MIN_VALID_OVERLAP_PERCENT
) -> List[Dict[str, Any]]:
    """
    Calculate coverage of parcel across multiple zoning districts from WKB bytes.
    
    Filters out sliver polygons (overlaps below min_overlap_percent).
    
    Args:
        parcel_wkb: Parcel geometry in WKB bytes
        zoning_layers: List of (wkb_bytes, zoning_code) tuples
        min_overlap_percent: Minimum overlap percentage to consider valid
        
    Returns:
        List of zoning districts with coverage percentages (filtered and sorted)
    """
    parcel_geom = wkb.loads(parcel_wkb)
    
    zoning_geoms = []
    for zoning_wkb, zoning_code in zoning_layers:
        zoning_geom = wkb.loads(zoning_wkb)
        zoning_geoms.append((zoning_geom, zoning_code))
    
    return calculate_zoning_coverage(parcel_geom, zoning_geoms, min_overlap_percent)