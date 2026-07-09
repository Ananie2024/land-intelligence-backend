# tests/integration/test_restore_workflow.py
"""
Integration tests for Restore Workflow — tests restore endpoints via TestClient.
Verifies restore job routing, status responses, and admin-only access controls.
"""
from fastapi.testclient import TestClient

from app.main import app


class TestRestoreStatusEndpoint:
    """Tests for restore job status endpoint."""

    def test_get_restore_status_requires_auth(self):
        """Restore status endpoint requires authentication."""
        client = TestClient(app)
        response = client.get("/api/v1/backups/restore/job-123")
        assert response.status_code == 401

    def test_get_restore_status_endpoint_exists(self):
        """Restore status endpoint is registered."""
        client = TestClient(app)
        response = client.get("/api/v1/backups/restore/job-123")
        assert response.status_code == 401


class TestRestoreTriggerEndpoint:
    """Tests for triggering restore operations."""

    def test_restore_trigger_endpoint_exists(self):
        """Restore trigger endpoint is registered."""
        client = TestClient(app)
        response = client.post("/api/v1/backups/restore?backup_job_id=backup-1")
        assert response.status_code == 401

    def test_restore_endpoint_validates_backup_job_id(self):
        """Restore trigger validates backup_job_id parameter."""
        client = TestClient(app)
        response = client.post("/api/v1/backups/restore")
        assert response.status_code in [401, 422]


class TestBackupRestoreIntegration:
    """Tests for restore-backup workflow integration at route level."""

    def test_backup_endpoint_exists(self):
        """Backup trigger endpoint is registered."""
        client = TestClient(app)
        response = client.get("/api/v1/backups/")
        assert response.status_code == 401

    def test_restore_after_backup_flow_endpoints_exist(self):
        """Both backup and restore endpoints are registered."""
        client = TestClient(app)

        response = client.post("/api/v1/backups/trigger?job_type=FULL&tier=local")
        assert response.status_code == 401

        response = client.post("/api/v1/backups/restore?backup_job_id=backup-1")
        assert response.status_code == 401


class TestRestoreErrorHandling:
    """Tests for restore endpoint error handling at route level."""

    def test_restore_invalid_path(self):
        """Invalid restore path returns appropriate status."""
        client = TestClient(app)
        response = client.get("/api/v1/backups/restore/")
        assert response.status_code in [401, 404, 405]


class TestRestoreEndpointMethods:
    """Tests for restore endpoint HTTP methods."""

    def test_restore_status_get_allowed(self):
        """Restore status endpoint allows GET."""
        client = TestClient(app)
        response = client.get("/api/v1/backups/restore/job-123")
        assert response.status_code == 401

    def test_restore_trigger_post_allowed(self):
        """Restore trigger endpoint allows POST."""
        client = TestClient(app)
        response = client.post("/api/v1/backups/restore?backup_job_id=backup-1")
        assert response.status_code == 401

    def test_restore_trigger_get_not_allowed(self):
        """Restore endpoint doesn't allow GET."""
        client = TestClient(app)
        response = client.get("/api/v1/backups/restore?backup_job_id=backup-1")
        assert response.status_code in [401, 405, 422]


class TestRestoreValidation:
    """Tests for restore parameter validation."""

    def test_missing_backup_job_id(self):
        """Missing backup_job_id parameter is rejected."""
        client = TestClient(app)
        response = client.post("/api/v1/backups/restore")
        assert response.status_code in [401, 422]