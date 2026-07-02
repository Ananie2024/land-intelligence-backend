"""Unit tests for BackupOrchestrator."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.backup.backup_orchestrator import BackupOrchestrator
from app.models.backup_job import BackupJobStatus, BackupJob


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def orchestrator(mock_db):
    with patch("app.services.backup.backup_orchestrator.BackupJobRepository"), \
         patch("app.services.backup.backup_orchestrator.LocalBackupService"), \
         patch("app.services.backup.backup_orchestrator.CloudBackupService"), \
         patch("app.services.backup.backup_orchestrator.CloudDownloadService"), \
         patch("app.services.backup.backup_orchestrator.DatabaseRestoreService"), \
         patch("app.services.backup.backup_orchestrator.EmailNotifier"), \
         patch("app.services.backup.backup_orchestrator.BackupReporter"):
        orch = BackupOrchestrator(mock_db)
        orch.backup_job_repo = AsyncMock()
        orch.local_backup_service = AsyncMock()
        orch.cloud_backup_service_gcs = AsyncMock()
        orch.cloud_backup_service_b2 = AsyncMock()
        orch.cloud_downloader = MagicMock()
        orch.db_restore_service = MagicMock()
        orch.email_notifier = MagicMock()
        orch.reporter = MagicMock()
        return orch


@pytest.mark.asyncio
async def test_create_backup_job_local_success(orchestrator):
    create_data = MagicMock()
    create_data.tier = "local"
    create_data.source_path = "/data/db"
    create_data.job_type = "FULL"

    job = MagicMock(spec=BackupJob)
    job.id = uuid4()
    orchestrator.backup_job_repo.create.return_value = job
    orchestrator.local_backup_service.perform_backup.return_value = {
        "status": "COMPLETED",
        "file_size_bytes": 1024,
        "file_count": 10,
        "destination_path": "/backups/test.zip",
        "checksum": "abc123",
    }
    orchestrator.backup_job_repo.update.return_value = job

    result = await orchestrator.create_backup_job(create_data)
    assert orchestrator.local_backup_service.perform_backup.called


@pytest.mark.asyncio
async def test_create_backup_job_local_failure(orchestrator):
    create_data = MagicMock()
    create_data.tier = "local"
    create_data.source_path = "/data/db"
    create_data.job_type = "FULL"

    job = MagicMock(spec=BackupJob)
    job.id = uuid4()
    orchestrator.backup_job_repo.create.return_value = job
    orchestrator.local_backup_service.perform_backup.side_effect = RuntimeError("Disk full")

    result = await orchestrator.create_backup_job(create_data)
    assert orchestrator.backup_job_repo.update.called


@pytest.mark.asyncio
async def test_create_backup_job_cloud_gcs(orchestrator):
    create_data = MagicMock()
    create_data.tier = "cloud_gcs"
    create_data.source_path = "/data/db"
    create_data.job_type = "FULL"

    job = MagicMock(spec=BackupJob)
    job.id = uuid4()
    orchestrator.backup_job_repo.create.return_value = job
    orchestrator.cloud_backup_service_gcs.perform_backup.return_value = {
        "status": "COMPLETED",
        "file_size_bytes": 2048,
        "file_count": 5,
        "destination_path": "gcs://bucket/backup.zip",
        "checksum": "def456",
    }
    orchestrator.backup_job_repo.update.return_value = job

    result = await orchestrator.create_backup_job(create_data)
    assert orchestrator.cloud_backup_service_gcs.perform_backup.called


@pytest.mark.asyncio
async def test_create_backup_job_cloud_b2(orchestrator):
    create_data = MagicMock()
    create_data.tier = "cloud_b2"
    create_data.source_path = "/data/db"
    create_data.job_type = "FULL"

    job = MagicMock(spec=BackupJob)
    job.id = uuid4()
    orchestrator.backup_job_repo.create.return_value = job
    orchestrator.cloud_backup_service_b2.perform_backup.return_value = {
        "status": "COMPLETED",
    }
    orchestrator.backup_job_repo.update.return_value = job

    result = await orchestrator.create_backup_job(create_data)
    assert orchestrator.cloud_backup_service_b2.perform_backup.called


@pytest.mark.asyncio
async def test_create_backup_job_unknown_tier(orchestrator):
    create_data = MagicMock()
    create_data.tier = "unsupported"
    create_data.source_path = "/data/db"
    create_data.job_type = "FULL"

    job = MagicMock(spec=BackupJob)
    job.id = uuid4()
    orchestrator.backup_job_repo.create.return_value = job
    orchestrator.backup_job_repo.update.return_value = job

    result = await orchestrator.create_backup_job(create_data)
    assert orchestrator.backup_job_repo.update.called


@pytest.mark.asyncio
async def test_restore_from_backup_local(orchestrator):
    orchestrator.db_restore_service.restore.return_value = {
        "status": "COMPLETED",
        "tables_restored": 15,
    }

    result = await orchestrator.restore_from_backup(
        backup_path="/backups/test.sql",
        job_id=str(uuid4()),
        is_cloud=False,
    )
    assert result["status"] == "COMPLETED"
    assert result["tables_restored"] == 15


@pytest.mark.asyncio
async def test_restore_from_backup_cloud(orchestrator):
    orchestrator.cloud_downloader.download.return_value = {
        "status": "COMPLETED",
        "local_path": "/tmp/restore.sql",
    }
    orchestrator.db_restore_service.restore.return_value = {
        "status": "COMPLETED",
        "tables_restored": 15,
    }

    result = await orchestrator.restore_from_backup(
        backup_path="gcs://bucket/backup.sql",
        job_id=str(uuid4()),
        is_cloud=True,
    )
    assert result["status"] == "COMPLETED"
    assert orchestrator.cloud_downloader.download.called


@pytest.mark.asyncio
async def test_restore_from_backup_cloud_download_fails(orchestrator):
    orchestrator.cloud_downloader.download.return_value = {
        "status": "FAILED",
        "error_message": "Network error",
    }

    result = await orchestrator.restore_from_backup(
        backup_path="gcs://bucket/backup.sql",
        job_id=str(uuid4()),
        is_cloud=True,
    )
    assert result["status"] == "FAILED"


@pytest.mark.asyncio
async def test_list_backup_jobs(orchestrator):
    mock_jobs = [MagicMock(spec=BackupJob) for _ in range(3)]
    orchestrator.backup_job_repo.list.return_value = mock_jobs

    result = await orchestrator.list_backup_jobs(status="COMPLETED", skip=0, limit=10)
    assert len(result) == 3


@pytest.mark.asyncio
async def test_update_backup_job_status(orchestrator):
    job = MagicMock(spec=BackupJob)
    orchestrator.backup_job_repo.update.return_value = job

    result = await orchestrator.update_backup_job_status(
        str(uuid4()), BackupJobStatus.COMPLETED
    )
    assert result is not None


@pytest.mark.asyncio
async def test_get_backup_job_found(orchestrator):
    job = MagicMock(spec=BackupJob)
    job.id = uuid4()
    job.job_type = "FULL"
    job.status = "COMPLETED"
    job.tier = "local"
    job.source_path = "/data"
    job.destination_path = "/backup.zip"
    job.file_size_bytes = 100
    job.file_count = 5
    job.checksum = "abc"
    job.error_message = None
    job.started_at = datetime.now(timezone.utc)
    job.completed_at = datetime.now(timezone.utc)
    job.created_at = datetime.now(timezone.utc)
    orchestrator.backup_job_repo.get.return_value = job

    result = await orchestrator.get_backup_job(str(uuid4()))
    assert result is not None
    assert result["job_type"] == "FULL"


@pytest.mark.asyncio
async def test_get_backup_job_not_found(orchestrator):
    orchestrator.backup_job_repo.get.return_value = None
    result = await orchestrator.get_backup_job(str(uuid4()))
    assert result is None


@pytest.mark.asyncio
async def test_list_backups(orchestrator):
    mock_jobs = [MagicMock(spec=BackupJob) for _ in range(2)]
    for j in mock_jobs:
        j.id = uuid4()
        j.job_type = "FULL"
        j.status = "COMPLETED"
        j.tier = "local"
        j.source_path = "/data"
        j.destination_path = "/backup.zip"
        j.file_size_bytes = 100
        j.file_count = 5
        j.checksum = "abc"
        j.error_message = None
        j.started_at = datetime.now(timezone.utc)
        j.completed_at = datetime.now(timezone.utc)
        j.created_at = datetime.now(timezone.utc)
    orchestrator.backup_job_repo.list.return_value = mock_jobs

    result = await orchestrator.list_backups()
    assert len(result) == 2


@pytest.mark.asyncio
async def test_trigger_restore_backup_not_found(orchestrator):
    orchestrator.backup_job_repo.get.return_value = None
    with pytest.raises(ValueError, match="not found"):
        await orchestrator.trigger_restore(str(uuid4()), "user1")


@pytest.mark.asyncio
async def test_trigger_restore_backup_not_completed(orchestrator):
    job = MagicMock(spec=BackupJob)
    job.status = "FAILED"
    job.tier = "local"
    job.destination_path = "/backup.zip"
    orchestrator.backup_job_repo.get.return_value = job
    with pytest.raises(ValueError, match="completed"):
        await orchestrator.trigger_restore(str(uuid4()), "user1")