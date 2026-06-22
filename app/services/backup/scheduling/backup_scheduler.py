import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.backup_job import BackupJobStatus, BackupJob
from app.repositories.backup_job_repository import BackupJobRepository

logger = logging.getLogger(__name__)


class BackupScheduler:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = BackupJobRepository(db)

    async def get_next_pending_job(self) -> Optional[BackupJob]:
        result = await self.repo.db.execute(
            select(BackupJob).where(BackupJob.status == BackupJobStatus.PENDING.value).limit(1)
        )
        return result.scalar_one_or_none()
