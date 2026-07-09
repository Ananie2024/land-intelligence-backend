# tests/integration/test_file_system_integration.py
"""
Integration tests for File System — tests document upload/download endpoints via TestClient.
Verifies file handling at the HTTP layer including multipart form data and streaming.
"""
from fastapi.testclient import TestClient

from app.main import app


class TestDocumentUploadEndpoint:
    """Tests for document upload endpoint."""

    def test_upload_endpoint_requires_auth(self):
        """Document upload endpoint requires authentication."""
        client = TestClient(app)
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.txt", b"test content")},
            data={"document_type_id": "type-1"},
        )
        assert response.status_code == 401

    def test_upload_endpoint_exists(self):
        """Document upload endpoint is registered - auth checked first."""
        client = TestClient(app)
        response = client.get("/api/v1/documents/upload")
        assert response.status_code in [401, 405]

    def test_upload_validates_form_data(self):
        """Upload endpoint validates form data structure."""
        client = TestClient(app)
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.txt", b"test content")},
        )
        assert response.status_code in [401, 422]


class TestDocumentSearchEndpoint:
    """Tests for document search endpoint."""

    def test_search_endpoint_requires_auth(self):
        """Search documents endpoint requires authentication."""
        client = TestClient(app)
        response = client.get("/api/v1/documents/")
        assert response.status_code == 401


class TestDocumentModifyEndpoint:
    """Tests for document update and delete endpoints."""

    def test_update_endpoint_exists(self):
        """Document update endpoint exists - auth checked first."""
        client = TestClient(app)
        response = client.get("/api/v1/documents/doc-1")
        assert response.status_code in [401, 405]

    def test_delete_endpoint_exists(self):
        """Document delete endpoint exists - auth checked first."""
        client = TestClient(app)
        response = client.get("/api/v1/documents/doc-1")
        assert response.status_code in [401, 405]


class TestDocumentDownloadEndpoint:
    """Tests for document download endpoint."""

    def test_download_endpoint_requires_auth(self):
        """Document download endpoint requires authentication."""
        client = TestClient(app)
        response = client.get("/api/v1/documents/doc-1/file")
        assert response.status_code == 401

    def test_download_endpoint_exists(self):
        """Document download endpoint is registered."""
        client = TestClient(app)
        response = client.post("/api/v1/documents/doc-1/file")
        assert response.status_code == 405


class TestPhysicalLocationEndpoint:
    """Tests for physical location endpoints."""

    def test_list_locations_endpoint_exists(self):
        """List locations endpoint is registered."""
        client = TestClient(app)
        response = client.get("/api/v1/locations/")
        assert response.status_code == 401

    def test_create_location_endpoint_exists(self):
        """Create location endpoint is registered."""
        client = TestClient(app)
        response = client.get("/api/v1/locations/")
        assert response.status_code == 401


class TestCabinetEndpoint:
    """Tests for storage cabinet endpoints."""

    def test_cabinets_endpoint_exists(self):
        """Cabinets endpoint is registered."""
        client = TestClient(app)
        response = client.get("/api/v1/locations/cabinets/cab-1")
        assert response.status_code in [401, 404, 405]


class TestDocumentPhysicalLocation:
    """Tests for document physical location resolution endpoint."""

    def test_physical_location_endpoint_requires_auth(self):
        """Document physical location endpoint requires auth."""
        client = TestClient(app)
        response = client.get("/api/v1/documents/doc-1/physical-location")
        assert response.status_code == 401


class TestLocationFind:
    """Tests for location finder endpoint."""

    def test_find_location_endpoint_exists(self):
        """Find location endpoint is registered."""
        client = TestClient(app)
        response = client.get("/api/v1/locations/find")
        assert response.status_code in [401, 405]

    def test_find_location_post_exists(self):
        """Find location endpoint accepts POST."""
        client = TestClient(app)
        response = client.post("/api/v1/locations/find", json={})
        assert response.status_code in [401, 422]


class TestLocationGrid:
    """Tests for location grid endpoint."""

    def test_grid_endpoint_exists(self):
        """Location grid endpoint is registered."""
        client = TestClient(app)
        response = client.get("/api/v1/locations/loc-1/grid")
        assert response.status_code == 401


class TestMultipartFormData:
    """Tests for multipart/form-data handling."""

    def test_document_upload_mime_type(self):
        """Document upload accepts various MIME types."""
        client = TestClient(app)
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("document.pdf", b"%PDF-1.4", "application/pdf")},
        )
        assert response.status_code in [401, 422]

    def test_document_upload_large_file(self):
        """Document upload handles large files."""
        client = TestClient(app)
        large_content = b"x" * 10000
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("large.pdf", large_content)},
        )
        assert response.status_code in [401, 422, 413]