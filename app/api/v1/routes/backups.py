# app/api/v1/routes/backups.py
"""
Backup Job API Routes
Phase 3 — Section 4.2
Land Intelligence System
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id
from app.repositories.backup_job_repository import BackupJobRepository
from app.models.backup_job import BackupJob, BackupJobStatus
from app.schemas.backup_job_schema import BackupJobCreate
from app.services.backup.backup_orchestrator import BackupOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=list[dict], summary="List backup jobs", description="List all backup jobs with optional status filter.")
async def list_backups(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = BackupJobRepository(db)
    filters = {}
    if status_filter:
        filters["status"] = status_filter
    skip = (page - 1) * size
    jobs = await repo.list(filters=filters, skip=skip, limit=size, order_by="created_at", descending=True)
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


@router.post("/trigger", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Trigger backup", description="Trigger a manual backup job.")
async def trigger_backup(
    job_type: str = Query("FULL", description="Backup type (FULL, INCREMENTAL, DIFFERENTIAL)"),
    tier: str = Query("local", description="Backup tier (local, cloud_gcs, cloud_b2)"),
    source_path: Optional[str] = Query(None, description="Source path to back up"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    orchestrator = BackupOrchestrator(db)
    job = await orchestrator.create_backup_job(
        BackupJobCreate(
            job_type=job_type.upper(),
            status=BackupJobStatus.PENDING,
            tier=tier.lower(),
            source_path=source_path,
        )
    )
    await db.commit()

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


@router.get("/jobs/{job_id}", response_model=dict, summary="Get job status", description="Get the status of a specific backup job.")
async def get_backup_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = BackupJobRepository(db)
    job = await repo.get(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Backup job '{job_id}' not found.")
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


@router.post("/restore", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Trigger restore", description="Trigger a restore from a backup job.")
async def trigger_restore(
    backup_job_id: str = Query(..., description="UUID of the backup job to restore from"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = BackupJobRepository(db)
    backup_job = await repo.get(backup_job_id)
    if not backup_job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Backup job '{backup_job_id}' not found.")
    if backup_job.status != BackupJobStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot restore from backup with status '{backup_job.status}'. Only completed backups can be restored.",
        )
    restore_job = BackupJob(
        job_type="RESTORE",
        status=BackupJobStatus.PENDING.value,
        tier=backup_job.tier,
        source_path=backup_job.destination_path,
    )
    db.add(restore_job)
    await db.flush()
    await db.refresh(restore_job)
    await db.commit()
    logger.info(f"Restore job triggered: {restore_job.id} from backup {backup_job_id} by user {user_id}")
    return {
        "id": str(restore_job.id),
        "status": restore_job.status,
        "source_backup_id": backup_job_id,
        "message": f"Restore job {restore_job.id} created and queued from backup {backup_job_id}.",
    }


@router.get("/restore/{job_id}", response_model=dict, summary="Get restore status", description="Get the status of a restore job.")
async def get_restore_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = BackupJobRepository(db)
    job = await repo.get(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Restore job '{job_id}' not found.")
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


