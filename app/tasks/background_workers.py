# app/tasks/background_workers.py
# app/tasks/background_workers.py
"""
Background Workers (Celery Tasks)
Land Intelligence System

All tasks are defined as standard synchronous Celery tasks that internally
call asyncio.run() to bridge into the async SQLAlchemy / service layer.

Available tasks
---------------
trigger_full_local_backup       — run a complete local 3-in-1 backup
trigger_backup_for_tier         — run a backup for a specific tier
check_latest_backup_integrity   — verify the most recent completed backup
retry_failed_backup_jobs        — re-queue failed jobs up to max retries
"""

import asyncio
import logging
from typing import Any

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal async helpers
# ---------------------------------------------------------------------------

async def _create_db_session():
    """Yield a single async database session for use inside a task."""
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        return session


async def _run_full_local_backup() -> dict[str, Any]:
    from app.core.database import AsyncSessionLocal
    from app.services.backup.local.local_backup_manager import LocalBackupManager
    from app.repositories.backup_job_repository import BackupJobRepository
    from app.schemas.backup_job_schema import BackupJobCreate
    from app.models.backup_job import BackupJobStatus

    async with AsyncSessionLocal() as db:
        repo = BackupJobRepository(db)
        job = await repo.create(
            BackupJobCreate(
                job_type="FULL",
                status=BackupJobStatus.PENDING,
                tier="local",
            )
        )
        await db.commit()
        await db.refresh(job)
        job_id = str(job.id)

    # Run backup outside the session to avoid long-held transactions
    manager = LocalBackupManager()
    result = await manager.run_full_backup(job_id)

    async with AsyncSessionLocal() as db:
        from app.schemas.backup_job_schema import BackupJobUpdate
        from app.models.backup_job import BackupJobStatus
        from datetime import datetime, timezone

        repo = BackupJobRepository(db)
        update = BackupJobUpdate(
            status=BackupJobStatus(result.get("status", "FAILED")),
            destination_path=result.get("destination_path"),
            file_size_bytes=result.get("file_size_bytes"),
            file_count=result.get("file_count"),
            checksum=result.get("checksum"),
            error_message=result.get("error_message"),
            completed_at=datetime.now(timezone.utc),
        )
        await repo.update(job_id, update)
        await db.commit()

    logger.info("Full local backup task finished for job %s: %s", job_id, result.get("status"))
    return {"job_id": job_id, "status": result.get("status")}


async def _check_latest_integrity() -> dict[str, Any]:
    from app.core.database import AsyncSessionLocal
    from app.repositories.backup_job_repository import BackupJobRepository
    from app.services.backup.validation.backup_verifier import BackupVerifier
    from app.services.backup.notifications.failure_alerter import FailureAlerter

    async with AsyncSessionLocal() as db:
        repo = BackupJobRepository(db)
        job = await repo.get_latest_completed_by_tier("local")

    if not job:
        logger.warning("Integrity check: no completed local backup found.")
        return {"status": "skipped", "reason": "no completed local backup"}

    verifier = BackupVerifier()
    passed = verifier.verify(job)

    if not passed:
        logger.error("Integrity check FAILED for backup job %s", job.id)
        FailureAlerter().alert(job)
        return {"job_id": str(job.id), "status": "FAILED"}

    logger.info("Integrity check PASSED for backup job %s", job.id)
    return {"job_id": str(job.id), "status": "PASSED"}


async def _retry_failed_jobs() -> dict[str, Any]:
    from app.core.database import AsyncSessionLocal
    from app.repositories.backup_job_repository import BackupJobRepository
    from app.services.backup.scheduling.retry_handler import RetryHandler

    async with AsyncSessionLocal() as db:
        repo = BackupJobRepository(db)
        failed_jobs = await repo.get_failed_jobs(limit=20)

    retried = 0
    for job in failed_jobs:
        async with AsyncSessionLocal() as db:
            handler = RetryHandler(db)
            await handler.handle(str(job.id))
            await db.commit()
            retried += 1

    logger.info("Retry task: processed %d failed jobs.", retried)
    return {"retried": retried}


# ---------------------------------------------------------------------------
# Celery task definitions
# ---------------------------------------------------------------------------

@celery_app.task(
    name="app.tasks.background_workers.trigger_full_local_backup",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
    queue="backup",
)
def trigger_full_local_backup(self) -> dict[str, Any]:
    """
    Celery task: run a full local backup (database + filesystem + config).
    Triggered daily by Celery Beat or manually via the API.
    """
    try:
        return asyncio.run(_run_full_local_backup())
    except Exception as exc:
        logger.error("trigger_full_local_backup failed: %s", exc, exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.background_workers.trigger_backup_for_tier",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
    queue="backup",
)
def trigger_backup_for_tier(self, tier: str, source_path: str | None = None) -> dict[str, Any]:
    """
    Celery task: trigger a backup job for a specific tier.

    Args:
        tier: 'local', 'cloud_gcs', or 'cloud_b2'
        source_path: optional override for source path
    """
    async def _run():
        from app.core.database import AsyncSessionLocal
        from app.services.backup.backup_orchestrator import BackupOrchestrator
        from app.schemas.backup_job_schema import BackupJobCreate
        from app.models.backup_job import BackupJobStatus

        async with AsyncSessionLocal() as db:
            orchestrator = BackupOrchestrator(db)
            job = await orchestrator.create_backup_job(
                BackupJobCreate(
                    job_type="FULL",
                    status=BackupJobStatus.PENDING,
                    tier=tier,
                    source_path=source_path,
                )
            )
            await db.commit()
            return {"job_id": str(job.id), "status": job.status}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("trigger_backup_for_tier(%s) failed: %s", tier, exc, exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.background_workers.check_latest_backup_integrity",
    bind=True,
    max_retries=1,
    queue="backup",
)
def check_latest_backup_integrity(self) -> dict[str, Any]:
    """
    Celery task: verify checksum and archive validity of the latest
    completed local backup job.
    """
    try:
        return asyncio.run(_check_latest_integrity())
    except Exception as exc:
        logger.error("check_latest_backup_integrity failed: %s", exc, exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.background_workers.retry_failed_backup_jobs",
    bind=True,
    max_retries=1,
    queue="maintenance",
)
def retry_failed_backup_jobs(self) -> dict[str, Any]:
    """
    Celery task: scan for FAILED backup jobs and re-queue them
    via RetryHandler (up to max_retries per job).
    """
    try:
        return asyncio.run(_retry_failed_jobs())
    except Exception as exc:
        logger.error("retry_failed_backup_jobs failed: %s", exc, exc_info=True)
        raise self.retry(exc=exc)