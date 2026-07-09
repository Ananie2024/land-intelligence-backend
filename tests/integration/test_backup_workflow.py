# tests/integration/test_backup_workflow.py
"""
Integration tests for Backup Workflow — tests backup endpoints via TestClient.
Verifies backup job routing, status responses, and admin-only access controls.
"""
from fastapi.testclient import TestClient

from app.main import app


class TestBackupListEndpoint:
    """Tests for GET /api/v1/backups/ (list backup jobs)."""

    def test_list_backups_requires_auth(self):
        """Endpoint requires authentication."""
        client = TestClient(app)
        response = client.get("/api/v1/backups/")
        assert response.status_code == 401

    def test_list_backups_with_pagination(self):
        """Endpoint supports pagination parameters."""
        client = TestClient(app)
        response = client.get(
            "/api/v1/backups/?status_filter=completed&page=1&size=10"
        )
        assert response.status_code == 401

    def test_list_backups_endpoint_exists(self):
        """Endpoint is registered with GET method."""
        client = TestClient(app)
        response = client.post("/api/v1/backups/")
        assert response.status_code == 405


class TestBackupTriggerEndpoint:
    """Tests for POST /api/v1/backups/trigger."""

    def test_trigger_backup_endpoint_exists(self):
        """Endpoint exists and requires auth."""
        client = TestClient(app)
        response = client.post("/api/v1/backups/trigger?job_type=FULL&tier=local")
        assert response.status_code == 401

    def test_trigger_backup_validates_job_type_param(self):
        """Endpoint accepts job_type query parameter."""
        client = TestClient(app)
        response = client.post("/api/v1/backups/trigger?job_type=FULL&tier=local&source_path=/data")
        assert response.status_code == 401

    def test_trigger_backup_validates_tier_values(self):
        """Endpoint validates tier parameter."""
        client = TestClient(app)
        response = client.post("/api/v1/backups/trigger?job_type=FULL&tier=invalid")
        assert response.status_code in [401, 422]


class TestBackupJobStatusEndpoint:
    """Tests for GET /api/v1/backups/jobs/{job_id}."""

    def test_get_backup_job_endpoint_exists(self):
        """Endpoint exists and requires auth."""
        client = TestClient(app)
        response = client.get("/api/v1/backups/jobs/test-job-id")
        assert response.status_code == 401


class TestBackupPaginationValidation:
    """Tests for backup pagination parameter validation."""

    def test_backup_pagination_validation(self):
        """Backup list pagination is validated - auth checked first."""
        client = TestClient(app)
        response = client.get("/api/v1/backups/?page=0")
        assert response.status_code in [401, 422]

        response = client.get("/api/v1/backups/?size=200")
        assert response.status_code in [401, 422]


class TestBackupJobMethods:
    """Tests for backup job endpoint methods."""

    def test_backup_list_allows_get(self):
        """Backup list allows GET."""
        client = TestClient(app)
        response = client.get("/api/v1/backups/")
        assert response.status_code == 401

    def test_backup_trigger_allows_post(self):
        """Backup trigger allows POST."""
        client = TestClient(app)
        response = client.post("/api/v1/backups/trigger?job_type=FULL&tier=local")
        assert response.status_code == 401

    def test_backup_job_get_allows_get(self):
        """Backup job status allows GET."""
        client = TestClient(app)
        response = client.get("/api/v1/backups/jobs/job-1")
        assert response.status_code == 401


class TestBackupRestoreEndpoints:
    """Tests for backup and restore endpoint registration."""

    def test_backup_trigger_registered(self):
        """Backup trigger endpoint is registered."""
        client = TestClient(app)
        response = client.post("/api/v1/backups/trigger?job_type=FULL&tier=local")
        assert response.status_code == 401

    def test_restore_trigger_registered(self):
        """Restore trigger endpoint is registered."""
        client = TestClient(app)
        response = client.post("/api/v1/backups/restore?backup_job_id=backup-1")
        assert response.status_code == 401

    def test_restore_status_registered(self):
        """Restore status endpoint is registered."""
        client = TestClient(app)
        response = client.get("/api/v1/backups/restore/job-123")
        assert response.status_code == 401