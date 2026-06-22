import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.backup_job_repository import BackupJobRepository
from app.services.backup.backup_orchestrator import BackupOrchestrator
from app.schemas.backup_job_schema import BackupJobCreate

logger = logging.getLogger(__name__)


class JobExecutor:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = BackupJobRepository(db)
        self.orchestrator = BackupOrchestrator(db)

    async def execute(self, job_id: str) -> None:
        logger.info("Executing backup job %s", job_id)
        job = await self.repo.get(job_id)
        if not job:
            logger.warning("Job %s not found", job_id)
            return
        create_data = BackupJobCreate(
            job_type=str(job.job_type),
            status=job.status,  # type: ignore[arg-type]
            tier=str(job.tier),
            source_path=job.source_path,  # type: ignore[arg-type]
        )
        await self.orchestrator.create_backup_job(create_data)
