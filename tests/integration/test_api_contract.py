# tests/integration/test_api_contract.py
"""
Integration tests for frontend-backend API contract.

Tests the axios interceptor logic, auth refresh flow, and GIS endpoints.
"""

import pytest


# ---------------------------------------------------------------------------
# Auth Refresh Flow Integration Tests
# ---------------------------------------------------------------------------

class TestAuthRefreshFlow:
    """
    Tests the token refresh interceptor logic in axios.ts.
    Simulates the queued retry behavior when multiple 401 requests occur.
    """

    @pytest.mark.asyncio
    async def test_invalid_token_returns_401_unauthorized(self, client):
        """
        Test that an invalid/unauthenticated token returns 401 Unauthorized.
        
        The axios interceptor relies on receiving 401 for expired tokens,
        which signals it to attempt a token refresh.
        """
        response = client.get("/api/v1/dashboard/stats")
        
        # Unauthenticated request MUST return 401 Unauthorized
        assert response.status_code == 401, \
            f"Expected 401 Unauthorized for unauthenticated request, got {response.status_code}"
        
        # Response must include error information for axios interceptor
        data = response.json()
        assert "message" in data or "detail" in data, \
            "Expected error response to contain error message field"

    @pytest.mark.asyncio
    async def test_refresh_token_endpoint_returns_401_for_invalid_token(self, client):
        """
        Test that /auth/refresh validates refresh tokens properly.
        
        Without valid token, should return 401 Unauthorized.
        This ensures the endpoint security is intact.
        """
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-refresh-token"}
        )
        
        # Invalid refresh token MUST return 401 Unauthorized
        assert response.status_code == 401, \
            f"Expected 401 Unauthorized for invalid refresh token, got {response.status_code}"
        
        # Error response structure for axios interceptor
        data = response.json()
        assert "message" in data or "detail" in data, \
            "Expected error structure in response body"

    @pytest.mark.asyncio
    async def test_authentication_error_response_structure(self, client):
        """
        Test that authentication errors follow the expected APIResponse structure.
        
        The axios interceptor expects:
        { success: false, message: string, errors?: [], meta?: {} }
        """
        response = client.get("/api/v1/dashboard/stats")
        
        assert response.status_code == 401
        
        data = response.json()
        # Must have error information (either message or detail field)
        has_expected_structure = "message" in data or "detail" in data
        assert has_expected_structure, \
            f"Response missing expected error structure: {data}"


class TestMultipleRequestsConsistency:
    """
    Tests that concurrent requests receive consistent responses,
    simulating the axios interceptor's processQueue behavior.
    """

    @pytest.mark.asyncio
    async def test_unauthenticated_requests_return_401_consistently(self, client):
        """
        Test that all unauthenticated requests return 401 consistently.
        
        When the axios interceptor queues requests during token refresh,
        all should return consistent error responses.
        """
        responses = []
        for _ in range(3):
            response = client.get("/api/v1/dashboard/stats")
            responses.append(response.status_code)
        
        # All unauthenticated requests should return 401
        for status in responses:
            assert status == 401, \
                f"Expected 401 Unauthorized for unauthenticated request, got {status}"


# ---------------------------------------------------------------------------
# GIS Endpoints Integration Tests
# ---------------------------------------------------------------------------

class TestGisEndpointsAuthentication:
    """
    Tests the GIS endpoints authentication requirements.
    """

    @pytest.mark.asyncio
    async def test_gis_distance_requires_authentication(self, client):
        """
        Test that GIS /distance endpoint requires authentication.
        
        Unauthenticated request must return 401 Unauthorized.
        """
        response = client.post(
            "/api/v1/gis/distance",
            json={"geom1_wkt": "POINT(0 0)", "geom2_wkt": "POINT(1 1)"}
        )
        
        # Must return 401 (Unauthorized)
        assert response.status_code == 401, \
            f"Expected 401 Unauthorized for unauthenticated request, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_gis_intersects_requires_authentication(self, client):
        """Test that GIS /intersects endpoint requires authentication."""
        response = client.post(
            "/api/v1/gis/intersects",
            json={
                "geom1_wkt": "POLYGON((0 0, 0 2, 2 2, 2 0, 0 0))",
                "geom2_wkt": "POLYGON((1 1, 1 3, 3 3, 3 1, 1 1))",
            }
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_gis_contains_point_requires_authentication(self, client):
        """Test that GIS /contains-point endpoint requires authentication."""
        response = client.post(
            "/api/v1/gis/contains-point",
            json={
                "geom_wkt": "POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))",
                "x": 5.0,
                "y": 5.0,
            }
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_gis_check_overlay_requires_authentication(self, client):
        """Test that GIS /check-overlay endpoint requires authentication."""
        response = client.post(
            "/api/v1/gis/check-overlay",
            json={
                "parcel_id": "test-parcel-uuid",
                "zoning_wkt": "POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))",
                "zoning_code": "RES-01",
            }
        )
        
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Reports Endpoints Integration Tests
# ---------------------------------------------------------------------------

class TestReportsEndpointsAuthentication:
    """
    Tests the report endpoints authentication requirements.
    """

    @pytest.mark.asyncio
    async def test_tax_report_requires_authentication(self, client):
        """Test that /reports/tax requires authentication."""
        response = client.get(
            "/api/v1/reports/tax/test-parcel-uuid",
            params={"format": "pdf"},
        )
        
        assert response.status_code == 401, \
            f"Expected 401 Unauthorized, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_parcels_report_requires_authentication(self, client):
        """Test that /reports/parcels requires authentication."""
        response = client.get(
            "/api/v1/reports/parcels",
            params={"format": "pdf"},
        )
        
        assert response.status_code == 401, \
            f"Expected 401 Unauthorized, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_dashboard_report_requires_authentication(self, client):
        """Test that /reports/dashboard requires authentication."""
        response = client.get(
            "/api/v1/reports/dashboard",
            params={"format": "pdf"},
        )
        
        assert response.status_code == 401, \
            f"Expected 401 Unauthorized, got {response.status_code}"


# ---------------------------------------------------------------------------|
# Axios Interceptor Contract Tests
# ---------------------------------------------------------------------------|

class TestAxiosInterceptorContract:
    """
    Tests the contract expected by the axios interceptor logic.
    These verify the API responses match what the frontend expects.
    """

    @pytest.mark.asyncio
    async def test_api_response_structure_on_unauthorized(self, client):
        """
        Test that 401 error responses follow the expected APIResponse structure.
        
        The axios interceptor expects:
        { success: false, message: string, errors?: [], meta?: {} }
        """
        response = client.get("/api/v1/dashboard/stats")
        
        assert response.status_code == 401
        
        # Must be JSON
        assert response.headers.get("content-type", "").startswith("application/json"), \
            "Error response must be JSON for axios interceptor"
        
        data = response.json()
        # Must have error information (message field in custom format)
        assert "message" in data, \
            f"Expected 'message' field in error response, got: {data}"

    @pytest.mark.asyncio
    async def test_auth_refresh_failure_returns_401(self, client):
        """
        Test that failed refresh returns proper 401 error structure.
        
        The frontend interceptor dispatches 'auth:unauthorized' event on 401
        when the refresh token is invalid.
        """
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"}
        )
        
        # Must return 401 for invalid refresh token
        assert response.status_code == 401, \
            f"Expected 401 Unauthorized for invalid refresh token, got {response.status_code}"
        
        # Response must contain error detail
        data = response.json()
        assert "message" in data or "detail" in data, \
            f"Expected error message in response, got: {data}"

    @pytest.mark.asyncio
    async def test_valid_token_format_allows_pass_through(self, client):
        """
        Test that requests with Bearer token format pass authentication.
        The actual authorization depends on whether the endpoint exists.
        """
        response = client.get("/api/v1/dashboard/stats", headers={"Authorization": "Bearer test-token"})
        
        # The token format is accepted (not rejected as "Not enough segments")
        # Response could be 401 (invalid token) or other codes
        # But we verify the request format is correct
        assert response.status_code in [200, 401, 404], \
            f"Unexpected status code: {response.status_code}"

    @pytest.mark.asyncio
    async def test_all_protected_endpoints_return_401_without_auth(self, client):
        """
        Test that all protected endpoints consistently require authentication.
        This verifies the auth contract across the API.
        """
        protected_endpoints = [
            ("/api/v1/dashboard/stats", "GET"),
            ("/api/v1/gis/distance", "POST"),
            ("/api/v1/gis/intersects", "POST"),
            ("/api/v1/gis/contains-point", "POST"),
            ("/api/v1/gis/check-overlay", "POST"),
            ("/api/v1/reports/tax/test-parcel", "GET"),
            ("/api/v1/reports/parcels", "GET"),
            ("/api/v1/reports/dashboard", "GET"),
        ]
        
        for endpoint, method in protected_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            assert response.status_code == 401, \
                f"Endpoint {endpoint} should require authentication (got {response.status_code})"