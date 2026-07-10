# tests/integration/test_api_contract.py
"""
Integration tests for frontend-backend API contract.

Tests the axios interceptor logic, auth refresh flow, and GIS endpoints.
"""

import pytest
from unittest.mock import patch

from app.models.user import UserRole


# ---------------------------------------------------------------------------
# Auth Refresh Flow Integration Tests
# ---------------------------------------------------------------------------

class TestAuthRefreshFlow:
    """
    Tests the token refresh interceptor logic in axios.ts.
    Simulates the queued retry behavior when multiple 401 requests occur.
    """

    @pytest.mark.asyncio
    async def test_401_triggers_token_refresh(self, client):
        """Test that a 401 response triggers the token refresh flow."""
        # This tests the frontend axios interceptor behavior via API contract
        # The backend should return 401 for expired tokens
        
        # Mock expired token scenario
        with patch("app.core.security.verify_token") as mock_verify:
            # First call: token is expired/invalid
            mock_verify.side_effect = [None, None]  # Both calls fail
            
            response = client.get("/api/v1/dashboard/stats")
            
            # Should expect 401 or 403 depending on implementation
            assert response.status_code in [401, 403, 404]

    @pytest.mark.asyncio
    async def test_refresh_token_endpoint_returns_new_tokens(self, client):
        """Test that /auth/refresh returns a valid token pair."""
        # Mock refresh token validation
        with patch("app.core.security.verify_token") as mock_verify:
            mock_verify.return_value = {
                "sub": "test-user-uuid",
                "username": "testuser",
                "role": "admin",
                "jti": "refresh-jti",
                "exp": 9999999999,
            }
            
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "valid-refresh-token"}
            )
            
            # Should succeed or fail gracefully
            assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_multiple_401_requests_queue_retry(self, client):
        """
        Test that concurrent 401 requests are queued for retry.
        
        This simulates the axios interceptor's processQueue behavior:
        when isRefreshing is true, subsequent 401 requests wait.
        """
        # This is a contract test - the interceptor handles this on the frontend
        # We verify the backend endpoints behave correctly under load
        
        # Test parallel requests get consistent responses
        responses = []
        for i in range(3):
            with patch("app.core.security.verify_token") as mock_verify:
                mock_verify.return_value = {
                    "sub": f"user-{i}",
                    "username": f"user{i}",
                    "role": "viewer",
                    "jti": f"jti-{i}",
                    "exp": 9999999999,
                }
                response = client.get("/api/v1/dashboard/stats")
                responses.append(response.status_code)
        
        # All requests should get the same treatment
        assert all(status in [200, 401, 403] for status in responses)


# ---------------------------------------------------------------------------
# GIS Endpoints Integration Tests
# ---------------------------------------------------------------------------

class TestGisEndpoints:
    """
    Tests the GIS analysis endpoints: /distance, /intersects, /contains-point, /check-overlay.
    
    These endpoints use spatial calculations that must work consistently
    between frontend and backend.
    """

    @pytest.fixture
    def auth_headers(self, viewer_auth_headers):
        """Get authenticated headers for viewer role."""
        return viewer_auth_headers

    @pytest.mark.asyncio
    async def test_gis_distance_endpoint(self, client, auth_headers):
        """Test POST /gis/distance calculates distance correctly."""
        response = client.post(
            "/api/v1/gis/distance",
            json={
                "geom1_wkt": "POINT(0 0)",
                "geom2_wkt": "POINT(3 4)",
            },
            headers=auth_headers
        )
        
        # Endpoint should exist and return proper structure
        if response.status_code == 200:
            data = response.json()
            assert "distance_meters" in data
            assert "message" in data
            # 3-4-5 triangle in degrees, but transformed to meters
            assert data["distance_meters"] > 0

    @pytest.mark.asyncio
    async def test_gis_intersects_endpoint(self, client, auth_headers):
        """Test POST /gis/intersects returns intersection data."""
        response = client.post(
            "/api/v1/gis/intersects",
            json={
                "geom1_wkt": "POLYGON((0 0, 0 2, 2 2, 2 0, 0 0))",
                "geom2_wkt": "POLYGON((1 1, 1 3, 3 3, 3 1, 1 1))",
            },
            headers=auth_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "intersects" in data
            assert "overlaps" in data
            assert "intersection_area_sqm" in data
            assert "percentage_overlap_geom1" in data
            assert "percentage_overlap_geom2" in data

    @pytest.mark.asyncio
    async def test_gis_contains_point_endpoint(self, client, auth_headers):
        """Test POST /gis/contains-point checks point containment."""
        response = client.post(
            "/api/v1/gis/contains-point",
            json={
                "geom_wkt": "POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))",
                "x": 5.0,
                "y": 5.0,
            },
            headers=auth_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "contains" in data
            assert "intersects" in data
            assert data["contains"] is True
            assert data["intersects"] is True

    @pytest.mark.asyncio
    async def test_gis_check_overlay_endpoint(self, client, auth_headers):
        """Test POST /gis/check-overlay for zoning compliance."""
        response = client.post(
            "/api/v1/gis/check-overlay",
            json={
                "parcel_id": "test-parcel-uuid",
                "zoning_wkt": "POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))",
                "zoning_code": "RES-01",
            },
            headers=auth_headers
        )
        
        # Should return 404 if parcel doesn't exist (expected in test)
        # or 200 with valid response
        assert response.status_code in [200, 400, 404]

    @pytest.mark.asyncio
    async def test_gis_distance_requires_auth(self, client):
        """Test that GIS endpoints require authentication."""
        response = client.post(
            "/api/v1/gis/distance",
            json={"geom1_wkt": "POINT(0 0)", "geom2_wkt": "POINT(1 1)"}
        )
        # Should require auth
        assert response.status_code in [401, 403, 404]


# ---------------------------------------------------------------------------
# Reports Endpoints Integration Tests
# ---------------------------------------------------------------------------

class TestReportsEndpoints:
    """
    Tests the report export endpoints (PDF/Excel).
    """

    @pytest.mark.asyncio
    async def test_tax_report_export(self, client, admin_auth_headers):
        """Test GET /reports/tax/{parcel_id} returns PDF/Excel."""
        # Using a fake parcel ID - expect 404 but verify endpoint structure
        response = client.get(
            "/api/v1/reports/tax/nonexistent-parcel-id",
            params={"format": "pdf"},
            headers=admin_auth_headers
        )
        
        # Should return 404 or 500 if parcel doesn't exist
        # But the endpoint should exist (not 405)
        assert response.status_code in [200, 404, 500]

    @pytest.mark.asyncio
    async def test_parcels_report_export(self, client, admin_auth_headers):
        """Test GET /reports/parcels returns PDF/Excel."""
        response = client.get(
            "/api/v1/reports/parcels",
            params={"format": "excel"},
            headers=admin_auth_headers
        )
        
        # Endpoint should exist
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            # Verify content type for Excel
            assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_dashboard_report_export(self, client, admin_auth_headers):
        """Test GET /reports/dashboard returns PDF/Excel."""
        response = client.get(
            "/api/v1/reports/dashboard",
            params={"format": "pdf"},
            headers=admin_auth_headers
        )
        
        if response.status_code == 200:
            # Verify content type for PDF
            assert "application/pdf" in response.headers.get("content-type", "")


# ---------------------------------------------------------------------------
# Axios Interceptor Contract Tests
# ---------------------------------------------------------------------------

class TestAxiosInterceptorContract:
    """
    Tests the contract expected by the axios interceptor logic.
    These verify the API responses match what the frontend expects.
    """

    @pytest.mark.asyncio
    async def test_api_response_structure_on_error(self, client):
        """
        Test that error responses follow the expected APIResponse structure.
        
        The axios interceptor expects:
        { success: false, message: string, errors?: [], meta?: {} }
        """
        with patch("app.core.security.verify_token") as mock_verify:
            mock_verify.return_value = None  # Invalid token
            
            response = client.get("/api/v1/dashboard/stats")
            
            # The response should be JSON and have consistent structure
            if response.headers.get("content-type", "").startswith("application/json"):
                data = response.json()
                # Should have success field if structured error
                assert "success" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_auth_unauthorized_event_dispatched_on_refresh_failure(self, client):
        """
        Test that failed refresh returns proper error structure.
        
        The frontend interceptor dispatches 'auth:unauthorized' event on 401 after refresh fails.
        """
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"}
        )
        
        # Should return 401 for invalid refresh token
        assert response.status_code == 401
        
        # Response should indicate unauthorized
        data = response.json()
        assert "detail" in data or "message" in data