# tests/unit/test_gis_exchange.py
"""
Unit tests for the GIS Bulk Import / Export Engine.

Covers Shapefile, KML(KMZ) and GeoJSON decode/encode round-trips through the
GisExchangeService, KMZ-specific behaviour (zip container, doc.kml preference,
overlay discovery, error handling) and the export media-type dispatch.
"""
from __future__ import annotations

import asyncio
import io
import zipfile

import pytest
from shapely.geometry import Polygon

from app.services.gis.data_exchange import kml_io
from app.services.gis.data_exchange.base import GisDataset, WGS84_CRS
from app.services.gis.data_exchange.exchange_service import (
    GisExchangeService,
    SUPPORTED_FORMATS,
)
from app.services.gis.data_exchange.rlmua_profile import normalize_properties
import app.api.v1.routes.gis_exchange as gex


# ---------------------------------------------------------------------------
# Shared geometry fixture
# ---------------------------------------------------------------------------

POLY = Polygon([(30.07, -2.27), (30.08, -2.27), (30.08, -2.28), (30.07, -2.28), (30.07, -2.27)])


@pytest.fixture
def sample_dataset() -> GisDataset:
    ds = GisDataset(crs=WGS84_CRS)
    ds.add_feature(
        POLY,
        {"upi": "1/02/02/03/0001", "owner_name": "Niyonzima", "area_sqm": 100.0},
        feature_id="PARCEL-0001",
    )
    return ds


# ---------------------------------------------------------------------------
# Format support surface
# ---------------------------------------------------------------------------


class TestSupportedFormats:
    def test_kmz_is_a_supported_exchange_format(self):
        assert "kmz" in SUPPORTED_FORMATS

    def test_kmz_accepted_on_import_route(self):
        assert "kmz" in gex._SUPPORTED_IMPORT_FORMATS

    def test_export_kmz_endpoint_registered(self):
        # NOTE: routes are registered on the bare router without the "/gis"
        # prefix — that prefix is applied by app/api/v1/endpoints.py at
        # include_router time. We assert the bare paths here.
        paths = {r.path for r in gex.router.routes if hasattr(r, "path")}
        assert "/import" in paths
        assert "/export/kmz" in paths


# ---------------------------------------------------------------------------
# KMZ import / export
# ---------------------------------------------------------------------------


class TestKmzRoundTrip:
    def test_serialize_then_import_roundtrip(self, sample_dataset):
        kmz = GisExchangeService.serialize_kmz_bytes(sample_dataset, base_name="rlmua_export")
        assert kmz[:2] == b"PK"  # ZIP magic

        restored = GisExchangeService.import_kmz(kmz)
        assert len(restored.features) == 1
        feat = restored.features[0]
        assert feat.geometry.geom_type == "Polygon"
        assert feat.properties["upi"] == "1/02/02/03/0001"
        assert restored.properties["kmz_document"] == "rlmua_export.kml"

    def test_import_prefers_doc_kml_member(self, sample_dataset):
        # Build a KMZ with two KML members (doc.kml should win) + an overlay.
        kml_bytes = kml_io.dataset_to_kml_bytes(sample_dataset)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("other.kml", kml_bytes)
            archive.writestr("doc.kml", kml_bytes)
            archive.writestr("overlay.png", b"\x89PNG\r\n\x1a\n fake")
        raw = buf.getvalue()

        restored = GisExchangeService.import_kmz(raw)
        assert restored.properties["kmz_document"] == "doc.kml"
        assert restored.properties["kmz_overlays"] == ["overlay.png"]
        assert len(restored.features) == 1

    def test_empty_payload_rejected(self):
        with pytest.raises(ValueError, match="KMZ payload is empty"):
            GisExchangeService.import_kmz(b"")

    def test_non_zip_payload_rejected(self):
        with pytest.raises(ValueError, match="not a valid ZIP archive"):
            GisExchangeService.import_kmz(b"this is not a zip file")

    def test_zip_without_kml_rejected(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("readme.txt", b"no kml here")
        with pytest.raises(ValueError, match="no .kml document"):
            GisExchangeService.import_kmz(buf.getvalue())


# ---------------------------------------------------------------------------
# Regression: KML, GeoJSON and Shapefile round-trips
# ---------------------------------------------------------------------------


class TestOtherFormatsRoundTrip:
    def test_kml_roundtrip(self, sample_dataset):
        kml = GisExchangeService.serialize_kml_bytes(sample_dataset)
        restored = GisExchangeService.import_kml(kml)
        assert len(restored.features) == 1
        assert restored.features[0].geometry.geom_type == "Polygon"

    def test_geojson_roundtrip(self, sample_dataset):
        gj = GisExchangeService.serialize_geojson_bytes(sample_dataset)
        restored = GisExchangeService.import_geojson(gj)
        assert len(restored.features) == 1
        assert restored.features[0].properties["owner_name"] == "Niyonzima"

    def test_shapefile_roundtrip(self, sample_dataset):
        files = GisExchangeService.shapefile_files(sample_dataset)
        assert set(files) == {"shp", "shx", "dbf", "prj"}
        restored = GisExchangeService.import_shapefile(files["shp"], files["dbf"])
        assert len(restored.features) == 1
        assert restored.features[0].geometry.geom_type == "Polygon"


# ---------------------------------------------------------------------------
# Attribute mapping profile
# ---------------------------------------------------------------------------


class TestRlmuaMapping:
    def test_normalize_maps_variants_to_canonical_fields(self):
        raw = {"UPI": "1/02/02/03/0001", "OwnerName": "Uwimana", "AreaSqm": "120.5"}
        canonical, extra = normalize_properties(raw, profile="rlmua")
        assert canonical["upi"] == "1/02/02/03/0001"
        assert canonical["owner_name"] == "Uwimana"
        assert canonical["area_sqm"] == 120.5  # numeric coercion
        # Unmapped keys are preserved in `extra`, nothing lost.
        assert extra == {}


# ---------------------------------------------------------------------------
# Export dispatch (media type + filename) via the async export() entrypoint
# ---------------------------------------------------------------------------


class TestExportDispatch:
    @pytest.fixture
    def kmz_dataset(self):
        ds = GisDataset(crs=WGS84_CRS)
        ds.add_feature(POLY, {"upi": "1/02/02/03/0001"}, feature_id="p1")
        return ds

    def test_export_kmz_media_type_and_payload(self, kmz_dataset, monkeypatch, mock_db):
        async def _fake_collect(self, parish_id=None):
            return kmz_dataset

        monkeypatch.setattr(GisExchangeService, "collect_parcels", _fake_collect)

        svc = GisExchangeService(mock_db)
        media_type, filename, payload = asyncio.run(svc.export("kmz", base_name="rlmua_export"))

        assert media_type == "application/vnd.google-earth.kmz"
        assert filename == "rlmua_export.kmz"
        assert payload[:2] == b"PK"  # valid ZIP

    def test_export_unknown_format_raises(self, kmz_dataset, monkeypatch, mock_db):
        async def _fake_collect(self, parish_id=None):
            return kmz_dataset

        monkeypatch.setattr(GisExchangeService, "collect_parcels", _fake_collect)

        svc = GisExchangeService(mock_db)
        with pytest.raises(ValueError, match="Unsupported export format"):
            asyncio.run(svc.export("dxf"))
