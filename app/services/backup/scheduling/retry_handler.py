import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.backup_job import BackupJobStatus
from app.repositories.backup_job_repository import BackupJobRepository

logger = logging.getLogger(__name__)


class RetryHandler:
    def __init__(self, db: AsyncSession, max_retries: int = 3) -> None:
        self.repo = BackupJobRepository(db)
        self.max_retries = max_retries

    async def handle(self, job_id: str) -> None:
        job = await self.repo.get(job_id)
        if not job:
            return
        retries = getattr(job, "file_count", None) or 0
        if retries >= self.max_retries:
            logger.error("Job %s exceeded max retries", job_id)
            await self.repo.update(job_id, {
                "status": BackupJobStatus.FAILED.value,
                "error_message": "Max retries exceeded",
                "completed_at": datetime.now(timezone.utc),
            })
            return
        logger.info("Re-queuing job %s", job_id)
        await self.repo.update(job_id, {
            "job_type": job.job_type,
            "status": BackupJobStatus.PENDING.value,
            "tier": job.tier,
            "source_path": job.source_path,
        })
