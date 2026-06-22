import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backup_job import BackupJobStatus, BackupJob
from app.repositories.backup_job_repository import BackupJobRepository
from app.schemas.backup_job_schema import BackupJobCreate, BackupJobUpdate
from app.services.backup.local.local_backup_service import LocalBackupService
from app.services.backup.cloud.cloud_backup_service import CloudBackupService

logger = logging.getLogger(__name__)


class BackupOrchestrator:
    def __init__(self, db: AsyncSession):
        self.backup_job_repo = BackupJobRepository(db)
        self.local_backup_service = LocalBackupService()
        self.cloud_backup_service_gcs = CloudBackupService(cloud_provider="google_cloud_storage") # Example for GCS
        self.cloud_backup_service_b2 = CloudBackupService(cloud_provider="backblaze_b2") # Example for Backblaze B2

    async def create_backup_job(
        self, job_create_data: BackupJobCreate
    ) -> BackupJob:
        logger.info(f"Attempting to create backup job: {job_create_data.job_type} for tier {job_create_data.tier}")

        backup_job = await self.backup_job_repo.create(job_create_data)
        job_id_str = str(backup_job.id) # Convert UUID to string for services

        backup_result: Dict[str, Any] = {"status": "FAILED", "error_message": "No backup service handled the request."}

        if job_create_data.tier == "local":
            backup_result = await self.local_backup_service.perform_backup(
                source_path=job_create_data.source_path, # type: ignore
                job_id=job_id_str
            )
        elif job_create_data.tier == "cloud_gcs":
            backup_result = await self.cloud_backup_service_gcs.perform_backup(
                source_path=job_create_data.source_path, # type: ignore
                job_id=job_id_str
            )
        elif job_create_data.tier == "cloud_b2":
            backup_result = await self.cloud_backup_service_b2.perform_backup(
                source_path=job_create_data.source_path, # type: ignore
                job_id=job_id_str
            )
        else:
            logger.error(f"Unknown backup tier: {job_create_data.tier}")
            backup_result["error_message"] = f"Unknown backup tier: {job_create_data.tier}"

        # Update the backup job with the results
        update_data: dict[str, Any] = {
            "status": BackupJobStatus(backup_result.get("status", "FAILED")),
            "error_message": backup_result.get("error_message"),
            "file_size_bytes": backup_result.get("file_size_bytes"),
            "file_count": backup_result.get("file_count"),
            "destination_path": backup_result.get("destination_path"),
            "checksum": backup_result.get("checksum"),
        }

        status_is_terminal = (
            update_data["status"] == BackupJobStatus.COMPLETED
            or update_data["status"] == BackupJobStatus.FAILED
            or update_data["status"] == BackupJobStatus.CANCELLED
        )

        if status_is_terminal:
            update_data["completed_at"] = datetime.now(timezone.utc)

        updated_backup_job = await self.backup_job_repo.update(job_id_str, BackupJobUpdate(**update_data)) # type: ignore

        if updated_backup_job and updated_backup_job.status == BackupJobStatus.COMPLETED:
            logger.info(f"Backup job {job_id_str} successfully COMPLETED.")
        else:
            logger.error(f"Backup job {job_id_str} FAILED or partially failed. Error: {backup_result.get('error_message')}")
            
        return updated_backup_job if updated_backup_job else backup_job

    async def update_backup_job_status(
        self, job_id: str, status: BackupJobStatus, error_message: Optional[str] = None
    ) -> Optional[BackupJob]:
        update_data = BackupJobUpdate(status=status, error_message=error_message)
        if status in [BackupJobStatus.COMPLETED, BackupJobStatus.FAILED, BackupJobStatus.CANCELLED]:
            update_data.completed_at = datetime.now(timezone.utc)
        return await self.backup_job_repo.update(job_id, update_data)

    async def get_backup_job(self, job_id: str) -> Optional[BackupJob]:
        return await self.backup_job_repo.get(job_id)

    async def list_backup_jobs(
        self, 
        status: Optional[BackupJobStatus] = None,
        job_type: Optional[str] = None,
        tier: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[BackupJob]:
        filters: Dict[str, Any] = {}
        if status: filters["status"] = status
        if job_type: filters["job_type"] = job_type
        if tier: filters["tier"] = tier
        return await self.backup_job_repo.list(filters=filters, skip=skip, limit=limit)

    # Additional methods for handling different backup types and tiers will go here
    # e.g., trigger_local_backup, trigger_cloud_backup, handle_backup_completion, etc.
