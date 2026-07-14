"""Unit tests for cloud backup providers and services."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.backup.cloud.cloud_backup_service import CloudBackupService
from app.services.backup.cloud.cloud_download_service import CloudDownloadService
from app.services.backup.cloud.encryption_service import EncryptionService


class TestCloudBackupService:
    @pytest.fixture
    def service_gcs(self):
        with patch("app.services.backup.cloud.cloud_backup_service.GoogleCloudStorageProvider"),              patch("app.services.backup.cloud.cloud_backup_service.LocalBackupService"):
            svc = CloudBackupService("google_cloud_storage")
            svc.provider = MagicMock()
            svc.staging_backup_service = AsyncMock()
            svc.staging_backup_service.perform_backup.return_value = {"status": "COMPLETED", "destination_path": "/tmp/staging.zip"}
            return svc

    @pytest.fixture
    def service_b2(self):
        with patch("app.services.backup.cloud.cloud_backup_service.BackblazeB2Provider"),              patch("app.services.backup.cloud.cloud_backup_service.LocalBackupService"):
            svc = CloudBackupService("backblaze_b2")
            svc.provider = MagicMock()
            svc.staging_backup_service = AsyncMock()
            svc.staging_backup_service.perform_backup.return_value = {"status": "COMPLETED", "destination_path": "/tmp/staging.zip"}
            return svc

    @pytest.mark.asyncio
    async def test_perform_backup_gcs_calls_provider_upload(self, service_gcs):
        service_gcs.provider.upload.return_value = {"status": "COMPLETED"}
        await service_gcs.perform_backup(source_path="/data/db", job_id=str(uuid4()))
        assert service_gcs.provider.upload.called

    @pytest.mark.asyncio
    async def test_perform_backup_provider_failure(self, service_gcs):
        service_gcs.provider.upload.side_effect = RuntimeError("Upload failed")
        result = await service_gcs.perform_backup(source_path="/data/db", job_id=str(uuid4()))
        assert result["status"] == "FAILED"

    @pytest.mark.asyncio
    async def test_perform_backup_b2_calls_provider(self, service_b2):
        service_b2.provider.upload.return_value = {"status": "COMPLETED"}
        await service_b2.perform_backup(source_path="/data/db", job_id=str(uuid4()))
        assert service_b2.provider.upload.called


class TestCloudDownloadService:
    @pytest.fixture
    def service(self):
        with patch("app.services.backup.cloud.cloud_download_service.GoogleCloudStorageProvider"),              patch("app.services.backup.cloud.cloud_download_service.BackblazeB2Provider"):
            svc = CloudDownloadService()
            svc.provider = MagicMock()
            return svc

    def test_download_success(self, service):
        service.provider.download.return_value = {"status": "COMPLETED"}
        result = service.download("gcs://bucket/backup.sql", "/tmp/restore.sql")
        assert result["status"] == "COMPLETED"

    def test_download_failure(self, service):
        service.provider.download.side_effect = RuntimeError("Download failed")
        result = service.download("gcs://bucket/backup.sql", "/tmp/restore.sql")
        assert result["status"] == "FAILED"


class TestEncryptionService:
    @pytest.fixture
    def service(self):
        return EncryptionService()

    def test_encrypt_raises_file_not_found(self, service):
        with pytest.raises(FileNotFoundError):
            service.encrypt("/path/to/file")

    def test_decrypt_raises_file_not_found(self, service):
        with pytest.raises(FileNotFoundError):
            service.decrypt("/path/to/file")