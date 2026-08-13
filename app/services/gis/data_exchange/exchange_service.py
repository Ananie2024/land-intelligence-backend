# app/services/gis/data_exchange/exchange_service.py
"""
GIS Bulk Import / Export Service
Phase 3 — Section 4.3
Land Intelligence System

Orchestrates decoding of external GIS formats (Shapefile, KML, GeoJSON)
into the canonical GisDataset representation, reprojects source data into
WGS84 (EPSG:4326), maps RLMUA attribute names, and serializes datasets back
into the target exchange formats for seamless RLMUA integration.
"""

import io
import zipfile
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parcel import Parcel
from app.services.gis.data_exchange.base import GisDataset, GisFeature, WGS84_CRS
from app.services.gis.data_exchange import geojson_io, kml_io, shapefile_io
from app.services.gis.data_exchange.rlmua_profile import EXPORT_FIELD_NAMES, normalize_properties
from app.services.gis.spatial_analyzer import ensure_geometry
from app.utils.coordinate_transformations import transform_geometry

# WGS84 WKT used for the .prj sidecar written alongside shapefile exports.
_WGS84_PRJ_WKT = (
    'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],'
    'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
)

SUPPORTED_FORMATS = ("geojson", "json", "kml", "kmz", "shp", "shapefile")


class GisExchangeService:
    """Business logic layer for bulk GIS data exchange."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    @staticmethod
    def import_geojson(raw: bytes, source_crs: str = WGS84_CRS) -> GisDataset:
        """Decode GeoJSON bytes into a WGS84-normalized GisDataset."""
        dataset = geojson_io.geojson_to_dataset(raw)
        GisExchangeService._reproject(dataset, source_crs)
        return dataset

    @staticmethod
    def import_kml(raw: bytes, source_crs: str = WGS84_CRS) -> GisDataset:
        """Decode KML bytes into a WGS84-normalized GisDataset."""
        dataset = kml_io.kml_to_dataset(raw)
        GisExchangeService._reproject(dataset, source_crs)
        return dataset

    @staticmethod
    def import_kmz(raw: bytes, source_crs: str = WGS84_CRS) -> GisDataset:
        """Decode KMZ (zipped KML) bytes into a WGS84-normalized GisDataset."""
        dataset = kml_io.kmz_to_dataset(raw, source_crs)
        GisExchangeService._reproject(dataset, source_crs)
        return dataset

    @staticmethod
    def import_shapefile(shp: bytes, dbf: Optional[bytes] = None,
                         source_crs: str = WGS84_CRS) -> GisDataset:
        """Decode a Shapefile (.shp + optional .dbf) into a GisDataset."""
        features, file_crs = shapefile_io.read_shapefile(shp, dbf)
        declared_crs = source_crs or file_crs or WGS84_CRS
        dataset = GisDataset(crs=declared_crs, features=features)
        GisExchangeService._reproject(dataset, declared_crs)
        return dataset

    @staticmethod
    def _reproject(dataset: GisDataset, source_crs: str) -> None:
        """Reproject dataset features from source_crs into WGS84 when needed."""
        normalized_crs = (source_crs or WGS84_CRS).strip().upper()
        identity_crs = {"EPSG:4326", "4326", "WGS84", "WGS 84", ""}
        if normalized_crs in identity_crs:
            return

        for feature in dataset.features:
            if feature.geometry is None or feature.geometry.is_empty:
                continue
            try:
                feature.geometry = transform_geometry(feature.geometry, normalized_crs, WGS84_CRS)
            except Exception as exc:
                raise ValueError(
                    f"Could not transform geometry from {source_crs} to WGS84: {exc}"
                )
        dataset.crs = WGS84_CRS

    @staticmethod
    def normalize_dataset(dataset: GisDataset, profile: str = "rlmua") -> GisDataset:
        """
        Remap each feature's attributes onto canonical parcel fields.

        The canonical fields are merged on top of the original attributes so
        callers can rely on stable keys while preserving source data.
        """
        for feature in dataset.features:
            canonical, extra = normalize_properties(feature.properties, profile)
            merged: Dict[str, Any] = dict(extra)
            merged.update(canonical)
            feature.properties = merged
        return dataset

    @staticmethod
    def to_parcel_create_payload(feature: GisFeature) -> Dict[str, Any]:
        """
        Build a parcel creation payload (WKB-hex geometry + canonical fields)
        from a normalized feature, ready for ParcelRepository.create.
        """
        from app.utils.geometry_helpers import ensure_wkb_hex

        properties = feature.properties or {}
        payload: Dict[str, Any] = {
            "upi": properties.get("upi"),
            "owner_name": properties.get("owner_name"),
            "owner_contact": properties.get("owner_contact"),
            "area_sqm": properties.get("area_sqm"),
            "location_description": properties.get("location_description"),
            "valuation": properties.get("valuation"),
            "valuation_date": properties.get("valuation_date"),
        }
        if feature.geometry is not None and not feature.geometry.is_empty:
            payload["geometry_wkb"] = ensure_wkb_hex(feature.geometry)
    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    async def collect_parcels(self, parish_id: Optional[str] = None) -> GisDataset:
        """
        Load active parcels from the database into a GisDataset.

        Attributes are exported using RLMUA-friendly column names so the
        produced files can be shared with the Rwanda Land Management and
        Use Authority without transformation.
        """
        query = select(Parcel).where(Parcel.is_active)
        if parish_id:
            query = query.where(Parcel.parish_id == parish_id)
        result = await self.db.execute(query)
        parcels = result.scalars().all()

        dataset = GisDataset(
            crs=WGS84_CRS,
            properties={
                "name": "Land Intelligence Parcel Export",
                "description": "Exported for RLMUA integration (WGS84 / EPSG:4326)",
            },
        )

        for parcel in parcels:
            geometry = None
            if parcel.geometry_wkb is not None:
                try:
                    geometry = ensure_geometry(parcel.geometry_wkb)
                except Exception:
                    geometry = None

            properties: Dict[str, Any] = {
                EXPORT_FIELD_NAMES.get("upi", "upi"): parcel.upi,
                EXPORT_FIELD_NAMES.get("owner_name", "owner_name"): parcel.owner_name,
                EXPORT_FIELD_NAMES.get("owner_contact", "owner_contact"): parcel.owner_contact,
                EXPORT_FIELD_NAMES.get("area_sqm", "area_sqm"): parcel.area_sqm,
                EXPORT_FIELD_NAMES.get("land_use", "land_use"): (
                    parcel.land_use_category.name if parcel.land_use_category else None
                ),
                EXPORT_FIELD_NAMES.get("location_description", "location_description"): (
                    parcel.location_description
                ),
                EXPORT_FIELD_NAMES.get("valuation", "valuation"): parcel.valuation,
                EXPORT_FIELD_NAMES.get("valuation_date", "valuation_date"): (
                    parcel.valuation_date.isoformat() if parcel.valuation_date else None
                ),
            }
            if parcel.extra_data:
                properties.update(parcel.extra_data)

            dataset.add_feature(geometry, properties, feature_id=str(parcel.id))

        return dataset

    @staticmethod
    def serialize_geojson_bytes(dataset: GisDataset) -> bytes:
        """Serialize a dataset to pretty-printed GeoJSON bytes."""
        return geojson_io.dataset_to_geojson_bytes(dataset)

    @staticmethod
    def serialize_kml_bytes(dataset: GisDataset) -> bytes:
        """Serialize a dataset to KML bytes."""
        return kml_io.dataset_to_kml_bytes(dataset)

    @staticmethod
    def serialize_kmz_bytes(dataset: GisDataset, base_name: str = "doc") -> bytes:
        """Serialize a dataset to KMZ (zipped KML) bytes."""
        return kml_io.dataset_to_kmz_bytes(dataset, base_name)

    @staticmethod
    def shapefile_files(dataset: GisDataset) -> Dict[str, bytes]:
        """Serialize a dataset into a Shapefile file set (shp/shx/dbf/prj)."""
        shp, shx, dbf = shapefile_io.write_shapefile(dataset.features)
        return {
            "shp": shp,
            "shx": shx,
            "dbf": dbf,
            "prj": _WGS84_PRJ_WKT.encode("utf-8"),
        }

    @staticmethod
    def shapefile_zip(dataset: GisDataset, base_name: str = "rlmua_export") -> Tuple[str, bytes]:
        """Bundle a Shapefile file set into a single ZIP archive."""
        files = GisExchangeService.shapefile_files(dataset)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for extension, data in files.items():
                archive.writestr(f"{base_name}.{extension}", data)
        buffer.seek(0)
        return f"{base_name}.zip", buffer.read()

    async def export(
        self,
        export_format: str,
        parish_id: Optional[str] = None,
        base_name: str = "rlmua_export",
    ) -> Tuple[str, str, bytes]:
        """
        High-level export dispatch.

        Returns:
            Tuple of (media_type, filename, payload_bytes)
        """
        dataset = await self.collect_parcels(parish_id)
        fmt = export_format.strip().lower()

        if fmt in ("geojson", "json"):
            return (
                "application/geo+json",
                f"{base_name}.geojson",
                self.serialize_geojson_bytes(dataset),
            )
        if fmt in ("kml",):
            return (
                "application/vnd.google-earth.kml+xml",
                f"{base_name}.kml",
                self.serialize_kml_bytes(dataset),
            )
        if fmt == "kmz":
            return (
                "application/vnd.google-earth.kmz",
                f"{base_name}.kmz",
                self.serialize_kmz_bytes(dataset, base_name),
            )
        if fmt in ("shp", "shapefile"):
            filename, payload = self.shapefile_zip(dataset, base_name)
            return ("application/zip", filename, payload)

        raise ValueError(
            f"Unsupported export format '{export_format}'. "
            f"Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )
