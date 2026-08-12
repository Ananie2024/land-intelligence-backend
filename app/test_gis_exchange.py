# app/test_gis_exchange.py
"""
Unit tests for the GIS bulk import/export utilities (Shapefile, KML, GeoJSON).

These tests exercise the pure-CPU serialization path and require no database
connection. They live alongside the existing app/test_*.py convention.
"""

import io
import json as _json
import struct
import zipfile

from shapely.geometry import LineString, MultiPolygon, Point, Polygon

from app.services.gis.data_exchange import (
    GisDataset,
    geojson_to_dataset,
    dataset_to_kml,
    kml_to_dataset,
    read_shapefile,
    write_shapefile,
)
from app.services.gis.data_exchange.exchange_service import GisExchangeService
from app.services.gis.data_exchange.rlmua_profile import normalize_properties

OUTER = [(30.0, -2.0), (30.1, -2.0), (30.1, -1.9), (30.0, -1.9), (30.0, -2.0)]
HOLE = [(30.03, -1.97), (30.05, -1.97), (30.05, -1.95), (30.03, -1.95), (30.03, -1.97)]
EXPECTED_POLY_AREA = abs(Polygon(OUTER, [HOLE]).area)


def _sample_dataset():
    dataset = GisDataset()
    dataset.add_feature(Polygon(OUTER, [HOLE]), {"UPI": "1/02/02/03/1390", "OwnerName": "Mukiza"}, feature_id="p1")
    dataset.add_feature(Point(30.05, -1.95), {"name": "benchmark"}, feature_id="p2")
    return dataset


# ---------------------------------------------------------------------------
# GeoJSON
# ---------------------------------------------------------------------------
def test_geojson_round_trip():
    dataset = _sample_dataset()
    payload = GisExchangeService.serialize_geojson_bytes(dataset)
    restored = GisExchangeService.import_geojson(payload, "EPSG:4326")

    assert len(restored.features) == 2
    assert restored.features[0].geometry.geom_type == "Polygon"
    assert restored.features[0].properties["UPI"] == "1/02/02/03/1390"
    assert restored.features[1].geometry.geom_type == "Point"


def test_geojson_to_dataset_handles_collection():
    raw = (
        '{"type":"FeatureCollection","features":[{"type":"Feature",'
        '"geometry":{"type":"Point","coordinates":[30.0, -2.0]},'
        '"properties":{"name":"p"}}]}'
    ).encode("utf-8")
    dataset = geojson_to_dataset(raw)
    assert len(dataset.features) == 1
    assert dataset.features[0].has_geometry()


# ---------------------------------------------------------------------------
# KML
# ---------------------------------------------------------------------------
def test_kml_round_trip():
    dataset = _sample_dataset()
    kml_text = dataset_to_kml(dataset)
    restored = kml_to_dataset(kml_text.encode("utf-8"))

    assert len(restored.features) == 2
    assert restored.features[0].geometry.geom_type == "Polygon"
    assert abs(restored.features[0].geometry.area - EXPECTED_POLY_AREA) < 1e-9
    assert restored.features[1].geometry.geom_type == "Point"


def test_kml_namespaced_document():
    kml_text = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark><name>P1</name>'
        '<ExtendedData><Data name="UPI"><value>1/02/02/03/1400</value></Data></ExtendedData>'
        "<Polygon><outerBoundaryIs><LinearRing><coordinates>"
        "30.0,-2.0 30.1,-2.0 30.1,-1.9 30.0,-1.9 30.0,-2.0"
        "</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark></Document></kml>"
    )
    dataset = kml_to_dataset(kml_text.encode("utf-8"))
    assert len(dataset.features) == 1
    assert dataset.features[0].geometry is not None
    assert dataset.features[0].properties.get("UPI") == "1/02/02/03/1400"
# ---------------------------------------------------------------------------
# Shapefile
# ---------------------------------------------------------------------------
def test_shapefile_round_trip_with_hole_and_multipolygon():
    multipolygon = MultiPolygon([
        Polygon(OUTER, [HOLE]),
        Polygon([(30.2, -2.2), (30.25, -2.2), (30.25, -2.15), (30.2, -2.15), (30.2, -2.2)]),
    ])
    features = [
        {"geometry": Polygon(OUTER, [HOLE]), "properties": {"UPI": "1/02/02/03/1390", "OwnerName": "Mukiza", "AreaSqm": 1234.5}},
        {"geometry": multipolygon, "properties": {"UPI": "1/02/02/03/1400", "OwnerName": "Niyonzima", "AreaSqm": 5678.9}},
        {"geometry": Point(30.0, -2.0), "properties": {"name": "p3"}},
        {"geometry": LineString([(30.0, -2.0), (30.05, -2.05)]), "properties": {"name": "p4"}},
    ]
    from app.services.gis.data_exchange import GisFeature
    shp_features = [GisFeature(f["geometry"], dict(f["properties"])) for f in features]

    shp, shx, dbf = write_shapefile(shp_features)

    # header sanity: file code 9994 and polygon shape type 5
    assert struct.unpack(">i", shp[0:4])[0] == 9994
    assert struct.unpack("<i", shp[32:36])[0] == 5
    assert struct.unpack(">i", shx[0:4])[0] == 9994

    restored, _ = read_shapefile(shp, dbf)
    assert len(restored) == 4

    # polygon-with-hole preserved
    assert restored[0].geometry is not None
    assert abs(restored[0].geometry.area - EXPECTED_POLY_AREA) < 1e-9

    # multi-polygon preserved with two parts
    assert restored[1].geometry.geom_type == "MultiPolygon"
    assert len(restored[1].geometry.geoms) == 2

    # point/line features dropped (file is Polygon-typed) -> geometry None
    assert restored[2].geometry is None
    assert restored[3].geometry is None

    # attributes survive the round trip
    assert restored[0].properties["UPI"] == "1/02/02/03/1390"
    assert abs(float(restored[0].properties["AreaSqm"]) - 1234.5) < 1e-6


def test_shapefile_zip_bundle():
    dataset = _sample_dataset()
    filename, payload = GisExchangeService.shapefile_zip(dataset)
    assert filename.endswith(".zip")
    assert payload[:2] == b"PK"
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = set(archive.namelist())
        assert {"rlmua_export.shp", "rlmua_export.shx", "rlmua_export.dbf", "rlmua_export.prj"}.issubset(names)


# ---------------------------------------------------------------------------
# CRS reprojection
# ---------------------------------------------------------------------------
def test_import_reprojects_utm_to_wgs84():
    coords = [[[786500, 9852000], [786550, 9852000],
               [786550, 9852050], [786500, 9852050], [786500, 9852000]]]
    doc = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"UPI": "1/02/02/03/1500"},
             "geometry": {"type": "Polygon", "coordinates": coords}},
        ],
    }
    raw = _json.dumps(doc).encode("utf-8")

    dataset = GisExchangeService.import_geojson(raw, "EPSG:32735")
    centroid = dataset.features[0].geometry.centroid
    assert 20.0 < centroid.x < 40.0
    assert -5.0 < centroid.y < 0.0


# ---------------------------------------------------------------------------
# RLMUA profile
# ---------------------------------------------------------------------------
def test_rlmua_normalization():
    canonical, extra = normalize_properties({
        "ParcelUPI": "1/02/02/03/1600",
        "Owner": "Kayitare",
        "SHAPE_AREA": "4321.25",
        "Cell": "Nyamirambo",
    })
    assert canonical["upi"] == "1/02/02/03/1600"
    assert canonical["owner_name"] == "Kayitare"
    assert canonical["area_sqm"] == 4321.25
    assert canonical["location_description"] == "Nyamirambo"


def test_export_dispatch_methods():
    dataset = _sample_dataset()
    gj = GisExchangeService.serialize_geojson_bytes(dataset)
    kml = GisExchangeService.serialize_kml_bytes(dataset)
    assert gj.startswith(b"{") and b"FeatureCollection" in gj
    assert kml.lstrip().startswith(b"<?xml") and b"<Placemark>" in kml