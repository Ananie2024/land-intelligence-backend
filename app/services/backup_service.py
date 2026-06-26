# app/services/backup_service.py
"""
Backup Service
Phase 3 — Section 4.2
Land Intelligence System
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backup_job import BackupJob, BackupJobStatus
from app.repositories.backup_job_repository import BackupJobRepository
from app.schemas.backup_job_schema import BackupJobCreate, BackupJobUpdate
from app.services.backup.backup_orchestrator import BackupOrchestrator

logger = logging.getLogger(__name__)


class BackupService:
    """
    Business logic layer for backup operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.backup_job_repo = BackupJobRepository(db)
        self.orchestrator = BackupOrchestrator(db)

    async def list_backups(
        self,
        status_filter: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> List[Dict[str, Any]]:
        """
        List all backup jobs with optional status filter.
        """
        filters = {}
        if status_filter:
            filters["status"] = status_filter
        skip = (page - 1) * size
        jobs = await self.backup_job_repo.list(filters=filters, skip=skip, limit=size, order_by="created_at", descending=True)
        result = []
        for job in jobs:
            result.append({
                "id": str(job.id),
                "job_type": job.job_type,
                "status": job.status,
                "tier": job.tier,
                "source_path": job.source_path,
                "destination_path": job.destination_path,
                "file_size_bytes": job.file_size_bytes,
                "file_count": job.file_count,
                "checksum": job.checksum,
                "error_message": job.error_message,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "created_at": job.created_at.isoformat() if job.created_at else None,
            })
        return result

    async def trigger_backup(
        self,
        job_type: str,
        tier: str,
        source_path: Optional[str],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Trigger a manual backup job.
        """
        job = await self.orchestrator.create_backup_job(
            BackupJobCreate(
                job_type=job_type.upper(),
                status=BackupJobStatus.PENDING,
                tier=tier.lower(),
                source_path=source_path,
            )
        )
        await self.db.commit()

        logger.info(f"Backup job triggered: {job.id} type={job_type} tier={tier} by user {user_id}")
        return {
            "id": str(job.id),
            "job_type": job.job_type,
            "status": job.status,
            "tier": job.tier,
            "source_path": job.source_path,
            "destination_path": job.destination_path,
            "file_size_bytes": job.file_size_bytes,
            "file_count": job.file_count,
            "checksum": job.checksum,
            "error_message": job.error_message,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "message": f"Backup job {job.id} finished with status {job.status}.",
        }

    async def get_backup_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a specific backup job.
        """
        job = await self.backup_job_repo.get(job_id)
        if not job:
            return None
        return {
            "id": str(job.id),
            "job_type": job.job_type,
            "status": job.status,
            "tier": job.tier,
            "source_path": job.source_path,
            "destination_path": job.destination_path,
            "file_size_bytes": job.file_size_bytes,
            "file_count": job.file_count,
            "checksum": job.checksum,
            "error_message": job.error_message,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }

    async def trigger_restore(self, backup_job_id: str, user_id: str) -> Dict[str, Any]:
        """
        Trigger a restore from a backup job.
        """
        backup_job = await self.backup_job_repo.get(backup_job_id)
        if not backup_job:
            raise ValueError(f"Backup job '{backup_job_id}' not found.")
        if backup_job.status != BackupJobStatus.COMPLETED.value:
            raise ValueError(
                f"Cannot restore from backup with status '{backup_job.status}'. Only completed backups can be restored."
            )

        restore_job = await self.backup_job_repo.create_by_dict({
            "job_type": "RESTORE",
            "status": BackupJobStatus.PENDING.value,
            "tier": backup_job.tier,
            "source_path": backup_job.destination_path,
        })
        await self.db.commit()
        logger.info(f"Restore job triggered: {restore_job.id} from backup {backup_job_id} by user {user_id}")
        return {
            "id": str(restore_job.id),
            "status": restore_job.status,
            "source_backup_id": backup_job_id,
            "message": f"Restore job {restore_job.id} created and queued from backup {backup_job_id}.",
        }

    async def get_restore_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a restore job.
        """
        job = await self.backup_job_repo.get(job_id)
        if not job:
            return None
        return {
            "id": str(job.id),
            "job_type": job.job_type,
            "status": job.status,
            "tier": job.tier,
            "source_path": job.source_path,
            "destination_path": job.destination_path,
            "error_message": job.error_message,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }