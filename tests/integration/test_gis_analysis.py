# tests/integration/test_gis_analysis.py
"""
Integration tests for GIS Analysis — exercises the full service layer flow
(GisAnalysisService → spatial utilities) without the HTTP/auth layer.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock
from shapely import wkt
from shapely.geometry import Polygon
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.gis.gis_service import GisAnalysisService
from app.services.gis.area_calculator import calculate_area_from_geometry
from app.utils.coordinate_transformations import to_metric


# ---------------------------------------------------------------------------
# Helpers / shared geometries
# ---------------------------------------------------------------------------

SQUARE_WKT = "POLYGON((0 0,0 1,1 1,1 0,0 0))"
OVERLAPPING_SQUARE_WKT = "POLYGON((0.5 0.5,0.5 2.5,2.5 2.5,2.5 0.5,0.5 0.5))"
DISJOINT_SQUARE_WKT = "POLYGON((10 10,10 11,11 11,11 10,10 10))"


@pytest.fixture
def mock_db():
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def service(mock_db):
    return GisAnalysisService(mock_db)


# ===================================================================
# _resolve_geometry
# ===================================================================

class TestResolveGeometry:
    async def test_resolves_from_wkt(self, service):
        geom = await service._resolve_geometry(SQUARE_WKT, None, "geom1")
        assert isinstance(geom, Polygon)
        assert geom.area > 0

    async def test_resolves_from_parcel_id(self, service, mock_db):
        parcel = MagicMock()
        parcel.geometry_wkb = wkt.loads(SQUARE_WKT).wkb

        async def _fake_get(parcel_id):
            return parcel

        service.parcel_repo.get = _fake_get
        # Ensure parcel_repo is already initialised on the service (it is, via fixture).
        geom = await service._resolve_geometry(None, "parcel-uuid-1", "geom1")
        assert isinstance(geom, Polygon)

    async def test_parcel_not_found_raises(self, service, mock_db):
        async def _fake_get(parcel_id):
            return None
        service.parcel_repo.get = _fake_get
        with pytest.raises(ValueError, match="not found"):
            await service._resolve_geometry(None, "bad-id", "geom1")

    async def test_no_geom_data_raises(self, service):
        with pytest.raises(ValueError, match="Either WKT or parcel ID must be specified"):
            await service._resolve_geometry(None, None, "geom1")

    async def test_invalid_wkt_raises(self, service):
        with pytest.raises(ValueError, match="Invalid WKT"):
            await service._resolve_geometry("BAD WKT", None, "geom1")

    async def test_parcel_without_geometry_raises(self, service, mock_db):
        parcel = MagicMock()
        parcel.geometry_wkb = None

        async def _fake_get(parcel_id):
            return parcel
        service.parcel_repo.get = _fake_get
        with pytest.raises(ValueError, match="does not have spatial geometry"):
            await service._resolve_geometry(None, "parcel-uuid-1", "geom1")


# ===================================================================
# calculate_distance
# ===================================================================

class TestCalculateDistance:
    async def test_same_geometry_is_zero(self, service):
        result = await service.calculate_distance(SQUARE_WKT, None, SQUARE_WKT, None)
        assert result["distance_meters"] == pytest.approx(0.0, abs=1e-3)

    async def test_disjoint_geometry_distance_positive(self, service):
        result = await service.calculate_distance(
            SQUARE_WKT, None, DISJOINT_SQUARE_WKT, None
        )
        assert result["distance_meters"] > 0

    async def test_missing_both_sides_raises(self, service):
        with pytest.raises(ValueError, match="Either WKT or parcel ID must be specified"):
            await service.calculate_distance(None, None, None, None)

    async def test_one_invalid_wkt_raises(self, service):
        with pytest.raises(ValueError, match="Invalid WKT"):
            await service.calculate_distance("BAD WKT", None, SQUARE_WKT, None)


# ===================================================================
# check_intersection
# ===================================================================

class TestCheckIntersection:
    async def test_overlapping_returns_true(self, service):
        result = await service.check_intersection(
            SQUARE_WKT, None, OVERLAPPING_SQUARE_WKT, None
        )
        assert result["intersects"] is True
        assert result["overlaps"] is True
        assert result["intersection_area_sqm"] > 0
        assert result["percentage_overlap_geom1"] > 0

    async def test_disjoint_returns_false(self, service):
        result = await service.check_intersection(
            SQUARE_WKT, None, DISJOINT_SQUARE_WKT, None
        )
        assert result["intersects"] is False
        assert result["overlaps"] is False
        assert result["intersection_area_sqm"] == 0.0
        assert result["percentage_overlap_geom1"] == 0.0

    async def test_touching_only_not_overlap(self, service):
        adj = "POLYGON((1 0,1 1,2 1,2 0,1 0))"
        result = await service.check_intersection(SQUARE_WKT, None, adj, None)
        assert result["intersects"] is True
        assert result["overlaps"] is False


# ===================================================================
# contains_point
# ===================================================================

class TestContainsPoint:
    async def test_inside_point(self, service):
        result = await service.contains_point(SQUARE_WKT, None, 0.5, 0.5)
        assert result["contains"] is True
        assert result["intersects"] is True

    async def test_outside_point(self, service):
        result = await service.contains_point(SQUARE_WKT, None, 100.0, 100.0)
        assert result["contains"] is False
        assert result["intersects"] is False

    async def test_boundary_point(self, service):
        result = await service.contains_point(SQUARE_WKT, None, 0.0, 0.0)
        assert result["contains"] is False
        assert result["intersects"] is True


# ===================================================================
# check_zoning_overlay
# ===================================================================

class TestCheckZoningOverlay:
    async def test_overlapping_parcel_and_zone(self, service):
        square = Polygon([(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)])
        original = GisAnalysisService._resolve_geometry
        async def _fake_resolve(self, *a, **kw):
            return square
        GisAnalysisService._resolve_geometry = _fake_resolve
        try:
            result = await service.check_zoning_overlay(
                "parcel-uuid-1",
                "POLYGON((0 0,0 2,2 2,2 0,0 0))",
                "RES-01",
            )
            assert result["intersects"] is True
            assert result["intersection_area"] > 0
            assert result["zoning_code"] == "RES-01"
        finally:
            GisAnalysisService._resolve_geometry = original

    async def test_non_overlapping_parcel_and_zone(self, service):
        square = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
        original = GisAnalysisService._resolve_geometry
        async def _fake_resolve(self, *a, **kw):
            return square
        GisAnalysisService._resolve_geometry = _fake_resolve
        try:
            result = await service.check_zoning_overlay(
                "parcel-uuid-1",
                "POLYGON((100 100,100 200,200 200,200 100,100 100))",
                "FAR-01",
            )
            assert result["intersects"] is False
            assert result["intersection_area"] == 0.0
        finally:
            GisAnalysisService._resolve_geometry = original

    async def test_invalid_zoning_wkt_raises(self, service):
        square = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
        original = GisAnalysisService._resolve_geometry
        async def _fake_resolve(self, *a, **kw):
            return square
        GisAnalysisService._resolve_geometry = _fake_resolve
        try:
            with pytest.raises(ValueError, match="Invalid WKT"):
                await service.check_zoning_overlay(
                    "parcel-uuid-1",
                    "NOT VALID WKT",
                    "RES-01",
                )
        finally:
            GisAnalysisService._resolve_geometry = original


# ===================================================================
# Service-level consistency checks (non-async helpers)
# ===================================================================

class TestServiceConsistency:
    def test_area_helper_uses_metric(self):
        """calculate_area_from_geometry with a WGS84 polygon returns degree-area (non-zero)."""
        poly = wkt.loads(SQUARE_WKT)
        area = calculate_area_from_geometry(poly)
        assert area > 0  # WGS84 degree-area
        # to_metric area should differ
        metric_area = to_metric(poly).area
        assert metric_area != area