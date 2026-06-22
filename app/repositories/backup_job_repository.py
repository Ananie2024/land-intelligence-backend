from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backup_job import BackupJob
from app.repositories.base_repository import BaseRepository
from app.schemas.backup_job_schema import BackupJobCreate, BackupJobUpdate


class BackupJobRepository(BaseRepository[BackupJob, BackupJobCreate, BackupJobUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(BackupJob, db)