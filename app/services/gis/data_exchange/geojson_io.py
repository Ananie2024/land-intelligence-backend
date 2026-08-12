# app/services/gis/data_exchange/geojson_io.py
"""
GeoJSON Import / Export Serializers
Phase 3 — Section 4.3
Land Intelligence System
"""

import json
from typing import Any, Dict, List, Optional

from shapely.geometry import shape, mapping
from shapely.geometry.base import BaseGeometry

from app.services.gis.data_exchange.base import GisDataset, GisFeature, WGS84_CRS

_GEOMETRY_TYPES = (
    "Point",
    "MultiPoint",
    "LineString",
    "MultiLineString",
    "Polygon",
    "MultiPolygon",
    "GeometryCollection",
)


def _extract_features(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalize any supported top-level GeoJSON document into a list of
    feature dictionaries.

    Supports FeatureCollection, single Feature, bare geometry objects and
    GeometryCollection documents.
    """
    if data is None:
        return []

    feature_type = data.get("type")
    if feature_type == "FeatureCollection":
        return list(data.get("features") or [])
    if feature_type == "Feature":
        return [data]
    if feature_type == "GeometryCollection":
        return [{"type": "Feature", "geometry": data, "properties": {}}]
    if feature_type in _GEOMETRY_TYPES:
        return [{"type": "Feature", "geometry": data, "properties": {}}]
    raise ValueError(f"Unsupported GeoJSON document type: {feature_type!r}")


def _geojson_crs(data: Dict[str, Any]) -> Optional[str]:
    """Extract the CRS name from a legacy GeoJSON `crs` member if present."""
    crs = data.get("crs")
    if isinstance(crs, dict):
        props = crs.get("properties") or {}
        return props.get("name") or props.get("href")
    return None


def geojson_to_dataset(raw: bytes, source_crs: str = WGS84_CRS) -> GisDataset:
    """
    Parse a GeoJSON document (bytes) into a GisDataset.

    Args:
        raw: UTF-8 encoded GeoJSON bytes
        source_crs: Declared CRS of the document when the file has no `crs` member

    Returns:
        GisDataset with one GisFeature per parsed feature
    """
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid GeoJSON payload: {exc}")

    dataset = GisDataset(crs=_geojson_crs(data) or source_crs)

    for feature_dict in _extract_features(data):
        geometry_dict = feature_dict.get("geometry")
        geometry: Optional[BaseGeometry] = None
        if geometry_dict:
            try:
                geometry = shape(geometry_dict)
            except Exception as exc:
                raise ValueError(f"Invalid GeoJSON geometry: {exc}")

        properties = feature_dict.get("properties") or {}
        feature_id = feature_dict.get("id")

        dataset.add_feature(geometry, dict(properties), feature_id)

    return dataset


def _feature_to_geojson(feature: GisFeature) -> Dict[str, Any]:
    """Serialize a single GisFeature into a GeoJSON Feature dictionary."""
    result: Dict[str, Any] = {"type": "Feature"}
    if feature.feature_id is not None:
        result["id"] = feature.feature_id
    if feature.has_geometry():
        result["geometry"] = mapping(feature.geometry)
    else:
        result["geometry"] = None
    result["properties"] = dict(feature.properties or {})
    return result


def dataset_to_geojson(dataset: GisDataset) -> Dict[str, Any]:
    """
    Serialize a GisDataset into a GeoJSON FeatureCollection dictionary.

    Args:
        dataset: Dataset to export

    Returns:
        GeoJSON FeatureCollection dictionary (JSON-serializable)
    """
    result: Dict[str, Any] = {
        "type": "FeatureCollection",
        "features": [_feature_to_geojson(f) for f in dataset.features],
    }
    # Preserve dataset-level metadata (excluding reserved GeoJSON keys)
    for key, value in (dataset.properties or {}).items():
        if key not in ("type", "features"):
            result[key] = value
    return result


def dataset_to_geojson_bytes(dataset: GisDataset, indent: Optional[int] = 2) -> bytes:
    """Serialize a dataset into compact/pretty GeoJSON bytes."""
    return json.dumps(dataset_to_geojson(dataset), indent=indent).encode("utf-8")
