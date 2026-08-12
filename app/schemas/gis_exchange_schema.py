# app/schemas/gis_exchange_schema.py
"""
GIS Bulk Import / Export Schemas
Phase 3 — Section 4.3
Land Intelligence System
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ImportedFeature(BaseModel):
    """
    One decoded feature returned from a bulk GIS import.

    Attributes:
        index: Zero-based position in the source file
        geometry_type: Shapely geometry type (None when geometry is missing)
        properties: Raw source attributes
        normalized: Canonical parcel fields after RLMUA mapping
    """

    index: int = Field(..., description="Zero-based feature position in the source file")
    geometry_type: Optional[str] = Field(None, description="Geometry type, e.g. 'Polygon'")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Raw source attributes")
    normalized: Dict[str, Any] = Field(default_factory=dict, description="Mapped canonical parcel fields")


class GisImportResponse(BaseModel):
    """
    Response summary for a bulk GIS import.

    Attributes:
        format: Imported exchange format (geojson | kml | shapefile)
        source_crs: CRS the source data was interpreted in
        total_features: Number of records found in the source
        imported: Features with a usable geometry
        skipped: Features without a usable geometry
        features: Per-feature decoding details
        errors: Non-fatal warnings collected during parsing
    """

    format: str = Field(..., description="Imported exchange format")
    source_crs: str = Field(..., description="CRS the source data was interpreted in")
    total_features: int = Field(..., ge=0, description="Number of records found in the source")
    imported: int = Field(..., ge=0, description="Features with a usable geometry")
    skipped: int = Field(..., ge=0, description="Features without a usable geometry")
    features: List[ImportedFeature] = Field(default_factory=list, description="Per-feature decoding details")
    errors: List[str] = Field(default_factory=list, description="Non-fatal warnings collected during parsing")
