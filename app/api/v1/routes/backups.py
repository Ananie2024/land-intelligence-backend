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
from app.api.auth_dependencies import get_current_user_id, require_admin
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
    orchestrator = BackupOrchestrator(db)
    result = await orchestrator.list_backups(status_filter=status_filter, page=page, size=size)
    return result


@router.post("/trigger", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Trigger backup", description="Trigger a manual backup job.")
async def trigger_backup(
    job_type: str = Query("FULL", description="Backup type (FULL, INCREMENTAL, DIFFERENTIAL)"),
    tier: str = Query("local", description="Backup tier (local, cloud_gcs, cloud_b2)"),
    source_path: Optional[str] = Query(None, description="Source path to back up"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    _admin: str = Depends(require_admin),
):
    orchestrator = BackupOrchestrator(db)
    result = await orchestrator.trigger_backup(job_type=job_type, tier=tier, source_path=source_path, user_id=user_id)
    return result


@router.get("/jobs/{job_id}", response_model=dict, summary="Get job status", description="Get the status of a specific backup job.")
async def get_backup_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    orchestrator = BackupOrchestrator(db)
    job = await orchestrator.get_backup_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Backup job '{job_id}' not found.")
    return job


@router.post("/restore", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Trigger restore", description="Trigger a restore from a backup job.")
async def trigger_restore(
    backup_job_id: str = Query(..., description="UUID of the backup job to restore from"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    _admin: str = Depends(require_admin),
):
    orchestrator = BackupOrchestrator(db)
    result = await orchestrator.trigger_restore(backup_job_id, user_id)
    return result


@router.get("/restore/{job_id}", response_model=dict, summary="Get restore status", description="Get the status of a restore job.")
async def get_restore_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    orchestrator = BackupOrchestrator(db)
    job = await orchestrator.get_restore_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Restore job '{job_id}' not found.")
    return job
