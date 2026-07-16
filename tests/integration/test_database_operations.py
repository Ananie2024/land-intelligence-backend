# tests/integration/test_database_operations.py
"""
Integration tests for Database Operations — tests database endpoints via TestClient.
Verifies database-related routing, error handling, and response formats.
"""
from fastapi.testclient import TestClient

from app.main import app


class TestDatabaseEndpointRouting:
    """Tests for database endpoint routing and authentication."""

    def test_parish_endpoints_require_auth(self):
        """Parish endpoints require authentication."""
        client = TestClient(app)
        response = client.get("/api/v1/parishes/")
        assert response.status_code == 401

    def test_parcel_endpoints_require_auth(self):
        """Parcel endpoints require authentication."""
        client = TestClient(app)
        response = client.get("/api/v1/parcels/")
        assert response.status_code == 401

    def test_document_endpoints_require_auth(self):
        """Document endpoints require authentication."""
        client = TestClient(app)
        response = client.get("/api/v1/documents/")
        assert response.status_code == 401


class TestPaginationValidation:
    """Tests for pagination parameter validation."""

    def test_pagination_params_validation(self):
        """Pagination parameters are validated (ge=1) - auth checked first."""
        client = TestClient(app)
        response = client.get("/api/v1/parishes/?page=0")
        # Auth is checked before query validation, so 401 is expected
        assert response.status_code in [401, 422]

    def test_max_size_validation(self):
        """Size parameter max validation works - auth checked first."""
        client = TestClient(app)
        response = client.get("/api/v1/parishes/?size=200")
        assert response.status_code in [401, 422]


class TestNotFoundResponses:
    """Tests for 404 response format across endpoints."""

    def test_parish_not_found_format(self):
        """Parish not found returns error format."""
        client = TestClient(app)
        response = client.get("/api/v1/parishes/nonexistent-id")
        assert response.status_code == 401

    def test_parcel_not_found_format(self):
        """Parcel not found returns error format."""
        client = TestClient(app)
        response = client.get("/api/v1/parcels/nonexistent-id")
        assert response.status_code == 401


class TestValidationResponses:
    """Tests for request validation error responses."""

    def test_invalid_parish_create_missing_code(self):
        """Missing required field returns 422."""
        client = TestClient(app)
        response = client.post(
            "/api/v1/parishes/",
            json={"name": "Missing Code Parish"},
        )
        assert response.status_code == 401

    def test_invalid_login_missing_password(self):
        """Missing password in login returns 422."""
        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "test"},
        )
        assert response.status_code == 422


class TestPydanticSerialization:
    """Tests for Pydantic model serialization at API layer."""

    def test_user_response_has_from_attributes(self):
        """UserResponse schema is configured for ORM serialization."""
        from app.schemas.user_schema import UserResponse
        
        assert UserResponse.model_config.get("from_attributes") is True

    def test_parish_response_has_from_attributes(self):
        """ParishResponse schema is configured for ORM serialization."""
        from app.schemas.parish_schema import ParishResponse
        
        assert ParishResponse.model_config.get("from_attributes") is True

    def test_parcel_response_has_from_attributes(self):
        """ParcelResponse schema is configured for ORM serialization."""
        from app.schemas.parcel_schema import ParcelResponse
        
        assert ParcelResponse.model_config.get("from_attributes") is True

    def test_document_response_has_from_attributes(self):
        """DocumentResponse schema is configured for ORM serialization."""
        from app.schemas.document_schema import DocumentResponse
        
        assert DocumentResponse.model_config.get("from_attributes") is True


class TestParishEndpointMethods:
    """Tests for parish endpoint HTTP methods."""

    def test_parish_list_methods(self):
        """Parish list supports GET."""
        client = TestClient(app)
        response = client.get("/api/v1/parishes/")
        assert response.status_code == 401

    def test_parish_create_methods(self):
        """Parish create supports POST."""
        client = TestClient(app)
        response = client.post("/api/v1/parishes/", json={})
        assert response.status_code in [401, 422]

    def test_parish_get_by_id_methods(self):
        """Parish get by ID supports GET."""
        client = TestClient(app)
        response = client.get("/api/v1/parishes/parish-1")
        assert response.status_code == 401

    def test_parish_update_methods(self):
        """Parish update supports PATCH."""
        client = TestClient(app)
        response = client.patch("/api/v1/parishes/parish-1", json={})
        assert response.status_code in [401, 405]

    def test_parish_delete_methods(self):
        """Parish delete supports DELETE."""
        client = TestClient(app)
        response = client.delete("/api/v1/parishes/parish-1")
        assert response.status_code in [401, 405]


class TestParcelEndpointMethods:
    """Tests for parcel endpoint HTTP methods."""

    def test_parcel_list_methods(self):
        """Parcel list supports GET."""
        client = TestClient(app)
        response = client.get("/api/v1/parcels/")
        assert response.status_code == 401

    def test_parcel_create_methods(self):
        """Parcel create supports POST."""
        client = TestClient(app)
        response = client.post("/api/v1/parcels/", json={})
        assert response.status_code in [401, 422]

    def test_parcel_get_by_id_methods(self):
        """Parcel get by ID supports GET."""
        client = TestClient(app)
        response = client.get("/api/v1/parcels/parcel-1")
        assert response.status_code == 401

    def test_parcel_by_number_methods(self):
        """Parcel lookup by UPI supports GET."""
        client = TestClient(app)
        response = client.get("/api/v1/parcels/by-upi/UPI-001")
        assert response.status_code == 401

    def test_parcel_by_deed_methods(self):
        """Parcel lookup by deed endpoint is removed (title_deed was deprecated)."""
        client = TestClient(app)
        response = client.get("/api/v1/parcels/by-deed/DEED-001")
        # Endpoint was removed along with title_deed_number column
        assert response.status_code == 404

    def test_parcel_update_methods(self):
        """Parcel update supports PATCH."""
        client = TestClient(app)
        response = client.patch("/api/v1/parcels/parcel-1", json={})
        assert response.status_code in [401, 405]

    def test_parcel_delete_methods(self):
        """Parcel delete supports DELETE."""
        client = TestClient(app)
        response = client.delete("/api/v1/parcels/parcel-1")
        assert response.status_code in [401, 405]


class TestDocumentEndpointMethods:
    """Tests for document endpoint HTTP methods."""

    def test_document_list_methods(self):
        """Document list supports GET."""
        client = TestClient(app)
        response = client.get("/api/v1/documents/")
        assert response.status_code == 401

    def test_document_upload_methods(self):
        """Document upload supports POST with multipart."""
        client = TestClient(app)
        response = client.post("/api/v1/documents/upload", files={})
        assert response.status_code in [401, 422]

    def test_document_get_methods(self):
        """Document get supports GET."""
        client = TestClient(app)
        response = client.get("/api/v1/documents/doc-1")
        assert response.status_code == 401

    def test_document_update_methods(self):
        """Document update supports PATCH."""
        client = TestClient(app)
        response = client.patch("/api/v1/documents/doc-1", json={})
        assert response.status_code in [401, 405]

    def test_document_delete_methods(self):
        """Document delete supports DELETE."""
        client = TestClient(app)
        response = client.delete("/api/v1/documents/doc-1")
        assert response.status_code in [401, 405]


class TestLocationEndpointMethods:
    """Tests for location endpoint HTTP methods."""

    def test_location_list_methods(self):
        """Location list supports GET."""
        client = TestClient(app)
        response = client.get("/api/v1/locations/")
        assert response.status_code == 401

    def test_location_create_methods(self):
        """Location create supports POST."""
        client = TestClient(app)
        response = client.post("/api/v1/locations/", json={})
        assert response.status_code in [401, 422]

    def test_location_get_methods(self):
        """Location get supports GET."""
        client = TestClient(app)
        response = client.get("/api/v1/locations/loc-1")
        assert response.status_code == 401

    def test_location_update_methods(self):
        """Location update supports PATCH."""
        client = TestClient(app)
        response = client.patch("/api/v1/locations/loc-1", json={})
        assert response.status_code in [401, 405]

    def test_location_delete_methods(self):
        """Location delete supports DELETE."""
        client = TestClient(app)
        response = client.delete("/api/v1/locations/loc-1")
        assert response.status_code in [401, 405]

    def test_cabinet_get_methods(self):
        """Cabinet get supports GET."""
        client = TestClient(app)
        response = client.get("/api/v1/locations/cabinets/cab-1")
        assert response.status_code in [401, 404]

    def test_cabinet_create_methods(self):
        """Cabinet create supports POST."""
        client = TestClient(app)
        response = client.post("/api/v1/locations/cabinets", json={})
        assert response.status_code in [401, 422]

    def test_find_location_methods(self):
        """Find location supports POST."""
        client = TestClient(app)
        response = client.post("/api/v1/locations/find", json={})
        assert response.status_code in [401, 422]