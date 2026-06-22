from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backup_verification import BackupVerification
from app.repositories.base_repository import BaseRepository
from app.schemas.backup_verification_schema import (
    BackupVerificationCreate,
    BackupVerificationUpdate,
)


class BackupVerificationRepository(
    BaseRepository[BackupVerification, BackupVerificationCreate, BackupVerificationUpdate]
):
    def __init__(self, db: AsyncSession):
        super().__init__(BackupVerification, db)
