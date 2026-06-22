import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backup_job import BackupJobStatus, BackupJob
from app.repositories.backup_job_repository import BackupJobRepository
from app.schemas.backup_job_schema import BackupJobUpdate

logger = logging.getLogger(__name__)


class RestoreOrchestrator:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = BackupJobRepository(db)

    async def start_restore(self, source_backup_id: str, destination_path: str) -> Optional[BackupJob]:
        logger.info("Starting restore from backup %s", source_backup_id)
        restore_job = BackupJob(
            job_type="RESTORE",
            status=BackupJobStatus.PENDING.value,
            tier="local",
            source_path=destination_path,
        )
        self.repo.db.add(restore_job)
        await self.repo.db.flush()
        await self.repo.db.refresh(restore_job)
        await self.repo.db.commit()
        logger.info("Restore job created: %s", restore_job.id)
        return restore_job

    async def complete_restore(self, restore_job_id: str) -> Optional[BackupJob]:
        logger.info("Marking restore job %s completed", restore_job_id)
        update = BackupJobUpdate(
            status=BackupJobStatus.COMPLETED,
            completed_at=datetime.now(timezone.utc),
        )
        return await self.repo.update(restore_job_id, update)

    async def fail_restore(self, restore_job_id: str, error_message: str) -> Optional[BackupJob]:
        logger.error("Restore job %s failed: %s", restore_job_id, error_message)
        update = BackupJobUpdate(
            status=BackupJobStatus.FAILED,
            error_message=error_message,
            completed_at=datetime.now(timezone.utc),
        )
        return await self.repo.update(restore_job_id, update)
