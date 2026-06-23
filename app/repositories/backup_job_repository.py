# app/repositories/backup_job_repository.py
"""
Backup Job Repository
Land Intelligence System
"""

import logging
from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backup_job import BackupJob, BackupJobStatus
from app.repositories.base_repository import BaseRepository
from app.schemas.backup_job_schema import BackupJobCreate, BackupJobUpdate

logger = logging.getLogger(__name__)


class BackupJobRepository(BaseRepository[BackupJob, BackupJobCreate, BackupJobUpdate]):

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(BackupJob, db)

    async def get_by_status(
        self, status: BackupJobStatus, skip: int = 0, limit: int = 100
    ) -> List[BackupJob]:
        """Return all active jobs with the given status, newest first."""
        return await self.list(
            filters={"status": status.value},
            skip=skip, limit=limit,
            order_by="created_at", descending=True,
        )

    async def get_pending_jobs(self, limit: int = 50) -> List[BackupJob]:
        """Return queued jobs waiting to be executed, oldest first."""
        return await self.list(
            filters={"status": BackupJobStatus.PENDING.value},
            limit=limit, order_by="created_at", descending=False,
        )

    async def get_failed_jobs(self, limit: int = 50) -> List[BackupJob]:
        """Return failed jobs, newest first."""
        return await self.list(
            filters={"status": BackupJobStatus.FAILED.value},
            limit=limit, order_by="created_at", descending=True,
        )

    async def get_latest_completed_by_tier(self, tier: str) -> Optional[BackupJob]:
        """Return the most recently completed backup job for a given tier."""
        try:
            result = await self.db.execute(
                select(BackupJob)
                .where(
                    BackupJob.is_active,
                    BackupJob.tier == tier,
                    BackupJob.status == BackupJobStatus.COMPLETED.value,
                )
                .order_by(desc(BackupJob.completed_at))
                .limit(1)
            )
            return result.scalar_one_or_none()
        except Exception as exc:
            logger.error("Error fetching latest completed job for tier %s: %s", tier, exc)
            raise

    async def get_jobs_by_type(
        self, job_type: str, skip: int = 0, limit: int = 100
    ) -> List[BackupJob]:
        """Return all active jobs of a given type."""
        return await self.list(
            filters={"job_type": job_type.upper()},
            skip=skip, limit=limit,
            order_by="created_at", descending=True,
        )

    async def update_status(
        self,
        job_id: str,
        status: BackupJobStatus,
        error_message: Optional[str] = None,
    ) -> Optional[BackupJob]:
        """Convenience method to update only the status of a backup job."""
        update = BackupJobUpdate(status=status, error_message=error_message)
        return await self.update(job_id, update)