import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession

import os
from pathlib import Path
from app.models.backup_job import BackupJobStatus, BackupJob
from app.repositories.backup_job_repository import BackupJobRepository
from app.schemas.backup_job_schema import BackupJobCreate, BackupJobUpdate

# Existing services
from app.services.backup.local.local_backup_service import LocalBackupService
from app.services.backup.cloud.cloud_backup_service import CloudBackupService

# Newly implemented services
from app.services.backup.cloud.cloud_download_service import CloudDownloadService
from app.services.backup.restoration.database_restore_service import DatabaseRestoreService
from app.services.backup.notifications.email_notifier import EmailNotifier
from app.services.backup.notifications.backup_reporter import BackupReporter

logger = logging.getLogger(__name__)


class BackupOrchestrator:
    def __init__(self, db: AsyncSession):
        self.backup_job_repo = BackupJobRepository(db)
        self.local_backup_service = LocalBackupService()
        self.cloud_backup_service_gcs = CloudBackupService(cloud_provider="google_cloud_storage")
        self.cloud_backup_service_b2 = CloudBackupService(cloud_provider="backblaze_b2")
        
        # New services
        self.cloud_downloader = CloudDownloadService()
        self.db_restore_service = DatabaseRestoreService()
        self.email_notifier = EmailNotifier()
        self.reporter = BackupReporter()

    async def verify_backups(self) -> Dict[str, Any]:
        """Verify integrity of existing backup archives by checking file existence and checksums."""
        logger.info("Starting backup verification...")
        try:
            jobs = await self.backup_job_repo.list(
                filters={"status": BackupJobStatus.COMPLETED.value},
                skip=0, limit=1000, order_by="created_at", descending=True
            )
            total_size = 0
            verified = 0
            failed = 0
            for job in jobs:
                dest = job.destination_path
                if dest:
                    p = Path(dest)
                    if p.exists():
                        total_size += p.stat().st_size
                        verified += 1
                    else:
                        failed += 1
            total_size_mb = round(total_size / (1024 * 1024), 2)
            status = "healthy" if failed == 0 else "degraded"
            return {
                "status": status,
                "message": f"Verified {verified} backup(s), {failed} missing." if failed > 0 else f"All {verified} backup(s) intact.",
                "backup_count": verified + failed,
                "total_size_mb": total_size_mb,
            }
        except Exception as exc:
            logger.error(f"Backup verification failed: {exc}", exc_info=True)
            return {
                "status": "unhealthy",
                "message": f"Verification error: {str(exc)}",
                "backup_count": 0,
                "total_size_mb": 0.0,
            }

    async def create_backup_job(self, job_create_data: BackupJobCreate) -> BackupJob:
        logger.info(f"Attempting to create backup job: {job_create_data.job_type} for tier {job_create_data.tier}")

        backup_job = await self.backup_job_repo.create(job_create_data)
        job_id_str = str(backup_job.id)

        backup_result: Dict[str, Any] = {"status": "FAILED", "error_message": "No backup service handled the request."}

        try:
            if job_create_data.tier == "local":
                backup_result = await self.local_backup_service.perform_backup(
                    source_path=job_create_data.source_path,
                    job_id=job_id_str
                )
            elif job_create_data.tier == "cloud_gcs":
                backup_result = await self.cloud_backup_service_gcs.perform_backup(
                    source_path=job_create_data.source_path,
                    job_id=job_id_str
                )
            elif job_create_data.tier == "cloud_b2":
                backup_result = await self.cloud_backup_service_b2.perform_backup(
                    source_path=job_create_data.source_path,
                    job_id=job_id_str
                )
            else:
                logger.error(f"Unknown backup tier: {job_create_data.tier}")
                backup_result["error_message"] = f"Unknown backup tier: {job_create_data.tier}"

        except Exception as exc:
            logger.error(f"Backup execution failed for job {job_id_str}: {exc}", exc_info=True)
            backup_result = {"status": "FAILED", "error_message": str(exc)}

        # Update job record
        update_data: dict[str, Any] = {
            "status": BackupJobStatus(backup_result.get("status", "FAILED")),
            "error_message": backup_result.get("error_message"),
            "file_size_bytes": backup_result.get("file_size_bytes"),
            "file_count": backup_result.get("file_count"),
            "destination_path": backup_result.get("destination_path"),
            "checksum": backup_result.get("checksum"),
        }

        status_is_terminal = update_data["status"] in [
            BackupJobStatus.COMPLETED,
            BackupJobStatus.FAILED,
            BackupJobStatus.CANCELLED
        ]

        if status_is_terminal:
            update_data["completed_at"] = datetime.now(timezone.utc)

        updated_backup_job = await self.backup_job_repo.update(
            job_id_str, BackupJobUpdate(**update_data)
        )

        # === Send Notification ===
        try:
            final_job = updated_backup_job or backup_job
            await asyncio.to_thread(self.email_notifier.send_backup_notification, final_job)
        except Exception as notif_exc:
            logger.warning(f"Failed to send backup notification for job {job_id_str}: {notif_exc}")

        if updated_backup_job and updated_backup_job.status == BackupJobStatus.COMPLETED:
            logger.info(f"Backup job {job_id_str} successfully COMPLETED.")
        else:
            logger.error(f"Backup job {job_id_str} FAILED. Error: {backup_result.get('error_message')}")

        return updated_backup_job if updated_backup_job else backup_job

    # ==================== NEW: Restore Methods ====================

    async def restore_from_backup(
        self,
        backup_path: str,
        job_id: str,
        is_cloud: bool = False
    ) -> Dict[str, Any]:
        """Restore database from backup (local or cloud)."""
        logger.info(f"Starting restore job {job_id} from {'cloud' if is_cloud else 'local'} backup: {backup_path}")

        try:
            if is_cloud:
                local_path = f"/tmp/restore_{job_id}.sql"
                download_result = self.cloud_downloader.download(backup_path, local_path)
                if download_result.get("status") == "FAILED":
                    raise RuntimeError(f"Cloud download failed: {download_result.get('error_message')}")
                backup_path = local_path

            restore_result = self.db_restore_service.restore(backup_path, job_id)

            # Notify
            await asyncio.to_thread(self.email_notifier.send_backup_notification, 
                                  type('obj', (object,), {
                                      "id": job_id,
                                      "job_type": "RESTORE",
                                      "status": restore_result["status"]
                                  })())

            return restore_result

        except Exception as exc:
            logger.error(f"Restore failed for job {job_id}: {exc}", exc_info=True)
            await asyncio.to_thread(self.email_notifier.send_backup_notification, 
                                  type('obj', (object,), {
                                      "id": job_id,
                                      "job_type": "RESTORE",
                                      "status": "FAILED",
                                      "error_message": str(exc)
                                  })())
            return {"status": "FAILED", "error_message": str(exc)}

    # Keep your existing helper methods
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

    async def list_backups(
        self,
        status_filter: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> List[Dict[str, Any]]:
        skip = (page - 1) * size
        filters: Dict[str, Any] = {}
        if status_filter:
            filters["status"] = status_filter
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
        from app.schemas.backup_job_schema import BackupJobCreate
        job = await self.create_backup_job(
            BackupJobCreate(
                job_type=job_type.upper(),
                status=BackupJobStatus.PENDING,
                tier=tier.lower(),
                source_path=source_path,
            )
        )
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

    async def trigger_restore(
        self,
        backup_job_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        from app.tasks.background_workers import trigger_restore_backup
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
        await self.backup_job_repo.db.commit()
        trigger_restore_backup.delay(str(restore_job.id))
        return {
            "id": str(restore_job.id),
            "status": restore_job.status,
            "source_backup_id": backup_job_id,
            "message": f"Restore job {restore_job.id} created and queued from backup {backup_job_id}.",
        }

    async def get_restore_job(self, job_id: str) -> Optional[Dict[str, Any]]:
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
