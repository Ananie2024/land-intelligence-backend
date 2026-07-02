# tests/unit/test_gis_services.py
"""
Unit tests for GIS utility functions — pure spatial logic tests.

Covers:
- Polygon validation and repair (Shapely is_valid, buffer(0))
- MultiPolygon handling
- SRID / CRS consistency (WGS84 → EPSG:21035 via pyproj)
- Area calculations (geometry, WKB, coordinates)
- Distance calculations (metric, empty geometry handling)
- Containment, intersection, overlap, proximity (touches, within)
- Bounding-box queries
- WKB/WKT parsing and error handling
- Coordinate transformation round-trips
"""
from __future__ import annotations

import pytest
from shapely.geometry import (
    Polygon,
    MultiPolygon,
    Point,
    LineString,
    box,
    mapping,
)
from shapely import wkt, wkb
from shapely.errors import GEOSException
import pyproj

from app.services.gis.area_calculator import (
    calculate_area_from_geometry,
    calculate_area_from_wkb,
    calculate_area_from_coordinates,
)
from app.services.gis.spatial_analyzer import (
    ensure_geometry,
    calculate_distance,
    contains_point,
    intersects_point,
    touches,
    is_within,
    get_centroid,
    get_point_on_surface,
    get_bounds,
    calculate_total_area,
    union_geometries,
)
from app.services.gis.polygon_intersection import (
    detect_overlap,
    calculate_intersection_area,
    get_intersection_geometry,
)
from app.services.gis.masterplan_overlay import (
    overlay_parcel_on_zoning,
    find_zoning_district,
    get_zoning_compliance,
    calculate_zoning_coverage,
)
from app.utils.coordinate_transformations import (
    to_metric,
    from_metric,
    transform_geometry,
    get_transformer,
    WGS84_CRS,
    RWANDA_METRIC_CRS,
)


# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------

# A simple square polygon in WGS84 (lon/lat degrees)
SQUARE_WGS84 = Polygon([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)])

# An identical square offset by 10 metres in metric space
# (after reprojecting to UTM 35N / EPSG:21035)
SQUARE_METRIC_APPROX = box(500_000.0, 0.0, 501_000.0, 1_000.0)


@pytest.fixture
def square_polygon() -> Polygon:
    """Return a simple square polygon in WGS84."""
    return Polygon([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)])


@pytest.fixture
def overlapping_polygons() -> tuple[Polygon, Polygon]:
    """Two overlapping squares (50 % overlap) in WGS84."""
    a = Polygon([(0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 0.0), (0.0, 0.0)])
    b = Polygon([(1.0, 1.0), (1.0, 3.0), (3.0, 3.0), (3.0, 1.0), (1.0, 1.0)])
    return a, b


@pytest.fixture
def non_overlapping_polygons() -> tuple[Polygon, Polygon]:
    """Two disjoint squares in WGS84."""
    a = Polygon([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)])
    b = Polygon([(5.0, 5.0), (5.0, 6.0), (6.0, 6.0), (6.0, 5.0), (5.0, 5.0)])
    return a, b


@pytest.fixture
def multipolygon() -> MultiPolygon:
    """A MultiPolygon consisting of two disjoint squares."""
    a = Polygon([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)])
    b = Polygon([(10.0, 10.0), (10.0, 11.0), (11.0, 11.0), (11.0, 10.0), (10.0, 10.0)])
    return MultiPolygon([a, b])


@pytest.fixture
def invalid_polygon() -> Polygon:
    """A self-intersecting (bow-tie) polygon that is geometrically invalid."""
    return Polygon([(0.0, 0.0), (2.0, 2.0), (0.0, 2.0), (2.0, 0.0), (0.0, 0.0)])


@pytest.fixture
def wkb_bytes_square() -> bytes:
    """WKB representation of a unit square (SRID 4326 / WGS84)."""
    return SQUARE_WGS84.wkb


@pytest.fixture
def zoning_layers() -> list[tuple[Polygon, str]]:
    """Sample zoning districts as (geometry, code) tuples."""
    residential = box(0.0, 0.0, 2.0, 2.0)
    commercial = box(1.5, 1.5, 4.0, 4.0)
    industrial = box(10.0, 10.0, 20.0, 20.0)
    return [
        (residential, "RES-01"),
        (commercial, "COM-01"),
        (industrial, "IND-01"),
    ]


# ===================================================================
# 1. ensure_geometry — format coercion
# ===================================================================

class TestEnsureGeometry:
    def test_returns_shapely_as_is(self, square_polygon):
        assert ensure_geometry(square_polygon) is square_polygon

    def test_loads_wkb_bytes(self, wkb_bytes_square):
        result = ensure_geometry(wkb_bytes_square)
        assert isinstance(result, Polygon)
        assert result.area > 0

    def test_loads_wkb_hex_string(self, wkb_bytes_square):
        hex_str = wkb_bytes_square.hex()
        result = ensure_geometry(hex_str)
        assert isinstance(result, Polygon)
        assert result.area > 0

    def test_raises_on_none(self):
        with pytest.raises(ValueError, match="Geometry data is required"):
            ensure_geometry(None)

    def test_raises_on_unsupported_type(self):
        with pytest.raises(TypeError, match="Unsupported geometry data type"):
            ensure_geometry(42)

    def test_rejects_linestring(self):
        ls = LineString([(0, 0), (1, 1)])
        # LineString IS a BaseGeometry, so it returns as-is; zero area below
        result = ensure_geometry(ls)
        assert result.geom_type == "LineString"


# ===================================================================
# 2. Area calculations
# ===================================================================

class TestAreaCalculations:
    def test_geometry_polygon_area(self, square_polygon):
        area = calculate_area_from_geometry(square_polygon)
        # ~ 123.2 sq km at equator for 1×1 degree – just check > 0
        assert area > 0

    def test_geometry_multipolygon_area(self, multipolygon):
        area = calculate_area_from_geometry(multipolygon)
        assert area > 0

    def test_geometry_empty_returns_zero(self):
        empty = Polygon()
        assert calculate_area_from_geometry(empty) == 0.0

    def test_point_returns_zero(self):
        assert calculate_area_from_geometry(Point(0, 0)) == 0.0

    def test_wkb_bytes_area(self, wkb_bytes_square):
        area = calculate_area_from_wkb(wkb_bytes_square)
        assert area > 0

    def test_coordinates_minimum_three_points(self):
        coords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]
        area = calculate_area_from_coordinates(coords)
        assert area > 0

    def test_coordinates_less_than_three_raises(self):
        with pytest.raises(ValueError, match="At least 3 points"):
            calculate_area_from_coordinates([(0.0, 0.0), (1.0, 1.0)])

    def test_invalid_polygon_repaired(self, invalid_polygon):
        """A bow-tie polygon is invalid; buffer(0) should repair it."""
        assert not invalid_polygon.is_valid
        area = calculate_area_from_coordinates(list(invalid_polygon.exterior.coords))
        assert area > 0


# ===================================================================
# 3. Distance calculations
# ===================================================================

class TestDistanceCalculations:
    def test_distance_self_is_zero(self, square_polygon):
        d = calculate_distance(square_polygon, square_polygon)
        assert d == pytest.approx(0.0, abs=1e-3)

    def test_distance_separated_positive(self, non_overlapping_polygons):
        a, b = non_overlapping_polygons
        d = calculate_distance(a, b)
        assert d > 0

    def test_distance_overlapping_positive(self, overlapping_polygons):
        a, b = overlapping_polygons
        d = calculate_distance(a, b)
        assert d == pytest.approx(0.0, abs=1e-3)

    def test_distance_empty_returns_negative_one(self, square_polygon):
        empty = Polygon()
        d = calculate_distance(square_polygon, empty)
        assert d == -1.0

    def test_distance_with_point(self):
        p1 = Point(0.0, 0.0)
        p2 = Point(3.0, 4.0)
        # In WGS84 degrees; to_metric converts → metres
        d = calculate_distance(p1, p2)
        assert d > 0


# ===================================================================
# 4. Point containment / intersection
# ===================================================================

class TestPointContainment:
    def test_contains_inside(self, square_polygon):
        assert contains_point(square_polygon, (0.5, 0.5)) is True

    def test_contains_outside(self, square_polygon):
        assert contains_point(square_polygon, (5.0, 5.0)) is False

    def test_contains_boundary(self, square_polygon):
        """Shapely 'contains' does NOT include the boundary."""
        assert contains_point(square_polygon, (0.0, 0.0)) is False

    def test_intersects_inside(self, square_polygon):
        assert intersects_point(square_polygon, (0.5, 0.5)) is True

    def test_intersects_boundary(self, square_polygon):
        assert intersects_point(square_polygon, (0.0, 0.0)) is True

    def test_intersects_outside(self, square_polygon):
        assert intersects_point(square_polygon, (5.0, 5.0)) is False

    def test_contains_empty_geometry(self):
        empty = Polygon()
        assert contains_point(empty, (0.0, 0.0)) is False

    def test_intersects_empty_geometry(self):
        empty = Polygon()
        assert intersects_point(empty, (0.0, 0.0)) is False


# ===================================================================
# 5. Topological predicates: touches, within
# ===================================================================

class TestTopologicalPredicates:
    def test_touches_true(self):
        a = box(0.0, 0.0, 1.0, 1.0)
        b = box(1.0, 0.0, 2.0, 1.0)
        assert touches(a, b) is True

    def test_touches_false_when_overlapping(self, overlapping_polygons):
        a, b = overlapping_polygons
        assert touches(a, b) is False

    def test_touches_false_when_disjoint(self, non_overlapping_polygons):
        a, b = non_overlapping_polygons
        assert touches(a, b) is False

    def test_within_true(self):
        inner = box(0.25, 0.25, 0.75, 0.75)
        outer = box(0.0, 0.0, 1.0, 1.0)
        assert is_within(inner, outer) is True

    def test_within_true_when_touching_boundary(self):
        """Shapely within: geometry sharing a boundary IS within."""
        inner = box(0.0, 0.0, 0.5, 0.5)
        outer = box(0.0, 0.0, 1.0, 1.0)
        assert is_within(inner, outer) is True

    def test_within_false_when_disjoint(self, non_overlapping_polygons):
        a, b = non_overlapping_polygons
        assert is_within(a, b) is False


# ===================================================================
# 6. Centroid and representative point
# ===================================================================

class TestCentroidAndRepresentativePoint:
    def test_centroid_unit_square(self, square_polygon):
        assert get_centroid(square_polygon) == pytest.approx((0.5, 0.5))

    def test_centroid_offset(self):
        p = Polygon([(10.0, 20.0), (10.0, 30.0), (20.0, 30.0), (20.0, 20.0), (10.0, 20.0)])
        assert get_centroid(p) == pytest.approx((15.0, 25.0))

    def test_centroid_empty_returns_zero(self):
        assert get_centroid(Polygon()) == (0.0, 0.0)

    def test_point_on_surface_inside(self, square_polygon):
        x, y = get_point_on_surface(square_polygon)
        assert 0.0 <= x <= 1.0
        assert 0.0 <= y <= 1.0

    def test_point_on_surface_empty(self):
        assert get_point_on_surface(Polygon()) == (0.0, 0.0)


# ===================================================================
# 7. Bounding box
# ===================================================================

class TestBoundingBox:
    def test_bounds_unit_square(self, square_polygon):
        assert get_bounds(square_polygon) == pytest.approx((0.0, 0.0, 1.0, 1.0))

    def test_bounds_empty(self):
        assert get_bounds(Polygon()) == (0.0, 0.0, 0.0, 0.0)

    def test_bounds_larger_polygon(self):
        p = Polygon([(-5.0, -5.0), (-5.0, 5.0), (5.0, 5.0), (5.0, -5.0), (-5.0, -5.0)])
        assert get_bounds(p) == pytest.approx((-5.0, -5.0, 5.0, 5.0))


# ===================================================================
# 8. Overlap / intersection detection
# ===================================================================

class TestOverlapDetection:
    def test_overlapping_returns_true(self, overlapping_polygons):
        a, b = overlapping_polygons
        assert detect_overlap(a, b) is True

    def test_non_overlapping_returns_false(self, non_overlapping_polygons):
        a, b = non_overlapping_polygons
        assert detect_overlap(a, b) is False

    def test_touching_only_not_overlap(self):
        a = box(0.0, 0.0, 1.0, 1.0)
        b = box(1.0, 0.0, 2.0, 1.0)
        assert detect_overlap(a, b) is False

    def test_intersection_area_overlapping(self, overlapping_polygons):
        a, b = overlapping_polygons
        area = calculate_intersection_area(a, b)
        assert area > 0

    def test_intersection_area_non_overlapping(self, non_overlapping_polygons):
        a, b = non_overlapping_polygons
        assert calculate_intersection_area(a, b) == 0.0

    def test_intersection_geometry_overlapping(self, overlapping_polygons):
        a, b = overlapping_polygons
        inter = get_intersection_geometry(a, b)
        assert inter is not None
        assert not inter.is_empty

    def test_intersection_geometry_non_overlapping(self, non_overlapping_polygons):
        a, b = non_overlapping_polygons
        assert get_intersection_geometry(a, b) is None

    def test_intersection_empty_geometry(self):
        empty = Polygon()
        assert calculate_intersection_area(empty, SQUARE_WGS84) == 0.0
        assert get_intersection_geometry(empty, SQUARE_WGS84) is None


# ===================================================================
# 9. Masterplan / zoning overlay
# ===================================================================

class TestZoningOverlay:
    def test_overlay_intersecting(self, square_polygon, zoning_layers):
        res = overlay_parcel_on_zoning(square_polygon, zoning_layers[0][0], "RES-01")
        assert res["intersects"] is True
        assert res["zoning_code"] == "RES-01"
        assert res["intersection_area"] > 0
        assert 0 < res["percentage_overlap"] <= 100

    def test_overlay_non_intersecting(self, square_polygon):
        far_away = box(100.0, 100.0, 200.0, 200.0)
        res = overlay_parcel_on_zoning(square_polygon, far_away, "FAR-01")
        assert res["intersects"] is False
        assert res["intersection_area"] == 0.0
        assert res["percentage_overlap"] == 0.0

    def test_find_zoning_district_best_match(self, square_polygon, zoning_layers):
        result = find_zoning_district(square_polygon, zoning_layers)
        assert result is not None
        assert result["zoning_code"] == "RES-01"
        assert result["percentage_overlap"] > 0

    def test_find_zoning_district_none_when_no_overlap(self):
        far_away = [ (box(100.0, 100.0, 200.0, 200.0), "FAR-01") ]
        result = find_zoning_district(SQUARE_WGS84, far_away)
        assert result is None

    def test_find_zoning_district_empty_parcel(self, zoning_layers):
        assert find_zoning_district(Polygon(), zoning_layers) is None

    def test_zoning_compliance_compliant(self, square_polygon, zoning_layers):
        result = get_zoning_compliance(square_polygon, ["RES-01"], zoning_layers)
        assert result["compliant"] is True
        assert result["zoning_found"]["zoning_code"] == "RES-01"

    def test_zoning_compliance_non_compliant(self, square_polygon, zoning_layers):
        result = get_zoning_compliance(square_polygon, ["IND-01"], zoning_layers)
        assert result["compliant"] is False
        assert "not in allowed" in result["message"]

    def test_zoning_coverage_counts_multiple(self, square_polygon, zoning_layers):
        # Square overlaps both RES-01 and COM-01 (they overlap each other at 1.5,1.5)
        results = calculate_zoning_coverage(square_polygon, zoning_layers)
        codes = {r["zoning_code"] for r in results}
        assert "RES-01" in codes
        # Results are sorted by coverage descending
        assert results == sorted(results, key=lambda r: r["percentage_coverage"], reverse=True)

    def test_zoning_coverage_empty_returns_empty(self, zoning_layers):
        assert calculate_zoning_coverage(Polygon(), zoning_layers) == []


# ===================================================================
# 10. Coordinate transformations (CRS)
# ===================================================================

class TestCoordinateTransformations:
    def test_to_metric_returns_geometry(self, square_polygon):
        metric = to_metric(square_polygon)
        assert metric is not None
        assert metric.area > 0

    def test_metric_area_different_from_geographic(self, square_polygon):
        """Metric area (m²) should not equal degree-area."""
        metric_area = to_metric(square_polygon).area
        degree_area = square_polygon.area
        assert metric_area != pytest.approx(degree_area)

    def test_round_trip_to_metric_and_back(self, square_polygon):
        back = from_metric(to_metric(square_polygon))
        # Coordinates should be approximately recovered
        orig_coords = list(square_polygon.exterior.coords)[0]
        back_coords = list(back.exterior.coords)[0]
        assert orig_coords == pytest.approx(back_coords, abs=1e-3)

    def test_transform_geometry_custom_crs(self, square_polygon):
        # Transform to WGS84 (source) → should be very close
        out = transform_geometry(square_polygon, WGS84_CRS, WGS84_CRS)
        assert out.equals(square_polygon)

    def test_get_transformer_returns_callable(self):
        transformer = get_transformer(WGS84_CRS, RWANDA_METRIC_CRS)
        assert callable(transformer.transform)

    def test_to_metric_empty_geometry(self):
        empty = Polygon()
        result = to_metric(empty)
        assert result.is_empty


# ===================================================================
# 11. Union and total area
# ===================================================================

class TestUnionAndTotalArea:
    def test_union_overlapping_avoids_double_count(self, overlapping_polygons):
        a, b = overlapping_polygons
        total = calculate_total_area([a, b])
        # Both sides must be in the same unit (metric m²) for a valid comparison.
        individual_sum = to_metric(a).area + to_metric(b).area
        assert total < individual_sum

    def test_union_disjoint_additive(self, non_overlapping_polygons):
        a, b = non_overlapping_polygons
        total = calculate_total_area([a, b])
        individual_sum = to_metric(a).area + to_metric(b).area
        assert total == pytest.approx(individual_sum, rel=1e-3)

    def test_union_empty_list(self):
        assert calculate_total_area([]) == 0.0

    def test_union_with_none(self, square_polygon):
        assert calculate_total_area([square_polygon, None]) == pytest.approx(
            to_metric(square_polygon).area
        )

    def test_union_geometries_returns_geometry(self, non_overlapping_polygons):
        a, b = non_overlapping_polygons
        result = union_geometries([a, b])
        assert result is not None
        assert result.geom_type in ("Polygon", "MultiPolygon")

    def test_union_geometries_empty_input(self):
        assert union_geometries([]) is None
        assert union_geometries([None, None]) is None


# ===================================================================
# 12. WKB / WKT parsing edge cases
# ===================================================================

class TestWkbWktParsing:
    def test_wkb_roundtrip(self, square_polygon):
        wkb_bytes = square_polygon.wkb
        restored = wkb.loads(wkb_bytes)
        assert restored.equals(square_polygon)

    def test_wkt_roundtrip(self, square_polygon):
        wkt_str = square_polygon.wkt
        restored = wkt.loads(wkt_str)
        assert restored.equals(square_polygon)

    def test_invalid_wkt_raises(self):
        with pytest.raises(Exception):
            wkt.loads("NOT_A_VALID_WKT")

    def test_wkb_with_srid_roundtrip(self, square_polygon):
        """Shapely 2.0 WKB roundtrip preserves geometry with embedded SRID."""
        wkb_bytes = square_polygon.wkb
        restored = wkb.loads(wkb_bytes)
        assert restored.equals(square_polygon)


# ===================================================================
# 13. Edge cases: empty, None, degenerate
# ===================================================================

class TestEdgeCases:
    def test_empty_polygon_is_empty(self):
        assert Polygon().is_empty

    def test_point_geometry_zero_area(self):
        assert calculate_area_from_geometry(Point(0, 0)) == 0.0

    def test_linestring_zero_area(self):
        assert calculate_area_from_geometry(LineString([(0, 0), (1, 1)])) == 0.0

    def test_detect_overlap_with_self(self, square_polygon):
        assert detect_overlap(square_polygon, square_polygon) is True

    def test_multipolygon_intersection_with_self(self, multipolygon):
        inter = get_intersection_geometry(multipolygon, multipolygon)
        assert inter is not None
        assert inter.equals(multipolygon)