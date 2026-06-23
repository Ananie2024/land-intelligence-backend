# app/repositories/backup_verification_repository.py
"""
Backup Verification Repository
Land Intelligence System
"""

import logging
from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backup_verification import BackupVerification, VerificationStatus
from app.repositories.base_repository import BaseRepository
from app.schemas.backup_verification_schema import (
    BackupVerificationCreate,
    BackupVerificationUpdate,
)

logger = logging.getLogger(__name__)


class BackupVerificationRepository(
    BaseRepository[BackupVerification, BackupVerificationCreate, BackupVerificationUpdate]
):

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(BackupVerification, db)

    async def get_by_backup_job_id(
        self, backup_job_id: str, skip: int = 0, limit: int = 100
    ) -> List[BackupVerification]:
        """Return all verifications for a backup job, newest first."""
        return await self.list(
            filters={"backup_job_id": backup_job_id},
            skip=skip, limit=limit,
            order_by="created_at", descending=True,
        )

    async def get_latest_by_backup_job_id(
        self, backup_job_id: str
    ) -> Optional[BackupVerification]:
        """Return the most recent verification record for a backup job."""
        try:
            result = await self.db.execute(
                select(BackupVerification)
                .where(
                    BackupVerification.is_active,
                    BackupVerification.backup_job_id == backup_job_id,
                )
                .order_by(desc(BackupVerification.created_at))
                .limit(1)
            )
            return result.scalar_one_or_none()
        except Exception as exc:
            logger.error(
                "Error fetching latest verification for job %s: %s", backup_job_id, exc
            )
            raise

    async def get_by_status(
        self, status: VerificationStatus, skip: int = 0, limit: int = 100
    ) -> List[BackupVerification]:
        """Return all verifications with the given status."""
        return await self.list(
            filters={"status": status.value},
            skip=skip, limit=limit,
            order_by="created_at", descending=True,
        )

    async def count_passed_for_job(self, backup_job_id: str) -> int:
        """Return the number of PASSED verifications for a backup job."""
        return await self.count(
            filters={
                "backup_job_id": backup_job_id,
                "status": VerificationStatus.PASSED.value,
            }
        )