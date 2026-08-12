# app/services/gis/data_exchange/base.py
"""
Common Data Structures for GIS Data Exchange
Phase 3 — Section 4.3
Land Intelligence System
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from shapely.geometry.base import BaseGeometry

# Default geographic CRS used across the Land Intelligence System.
# The parcels table stores geometries in WGS84 (EPSG:4326).
WGS84_CRS = "EPSG:4326"

# Rwandan national reference CRS (Arc 1960 / UTM zone 35S) used for metric
# area calculations. Imported data is always normalized into WGS84.
RWANDA_UTM_CRS = "EPSG:21035"


@dataclass
class GisFeature:
    """
    Canonical intermediate representation for a single GIS feature.

    Any external format (Shapefile, KML, GeoJSON) is decoded into this
    structure, and every export starts from it.

    Attributes:
        geometry: Shapely geometry (in WGS84 by convention)
        properties: Attribute dictionary (source-specific field names preserved)
        feature_id: Optional stable identifier for the feature
    """

    geometry: Optional[BaseGeometry] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    feature_id: Optional[str] = None

    def has_geometry(self) -> bool:
        """Return True when the feature carries a non-empty geometry."""
        return self.geometry is not None and not self.geometry.is_empty


@dataclass
class GisDataset:
    """
    Dataset-level container produced by import and consumed by export.

    Attributes:
        crs: Coordinate reference system the features are expressed in
        features: List of features in the dataset
        properties: Dataset-level metadata (e.g. name, description, source)
    """

    crs: str = WGS84_CRS
    features: List[GisFeature] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

    def add_feature(self, geometry: Optional[BaseGeometry], properties: Dict[str, Any],
                    feature_id: Optional[str] = None) -> None:
        """Convenience helper to append a feature to the dataset."""
        self.features.append(GisFeature(geometry=geometry, properties=properties, feature_id=feature_id))

    def __len__(self) -> int:
        return len(self.features)
