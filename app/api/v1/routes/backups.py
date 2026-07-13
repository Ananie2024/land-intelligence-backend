# app/api/v1/routes/backups.py
"""
Backup Job API Routes
Phase 3 — Section 4.2
Land Intelligence System
"""

import logging
import tempfile
import uuid
from typing import Optional, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import aiofiles
import asyncio

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id, require_admin
from app.services.backup.backup_orchestrator import BackupOrchestrator
from app.services.backup.cloud.cloud_download_service import CloudDownloadService

logger = logging.getLogger(__name__)

router = APIRouter()


async def _stream_file(file_path: Path) -> AsyncGenerator[bytes, None]:
    """Helper to stream a file as async generator."""
    async with aiofiles.open(file_path, 'rb') as f:
        while True:
            chunk = await f.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            yield chunk


async def _stream_and_cleanup(file_path: Path) -> AsyncGenerator[bytes, None]:
    """Stream a file and clean it up afterward."""
    try:
        async for chunk in _stream_file(file_path):
            yield chunk
    finally:
        try:
            await asyncio.get_event_loop().run_in_executor(None, file_path.unlink)
        except Exception:
            pass


@router.get("", response_model=list[dict], summary="List backup jobs", description="List all backup jobs with optional status filter.", include_in_schema=False)
async def list_backups_no_slash(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    orchestrator = BackupOrchestrator(db)
    result = await orchestrator.list_backups(status_filter=status_filter, page=page, size=size)
    return result


@router.get("/", response_model=list[dict], summary="List backup jobs", description="List all backup jobs with optional status filter.")
async def list_backups(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return await list_backups_no_slash(
        status_filter=status_filter, page=page, size=size, db=db, user_id=user_id
    )


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


@router.get("/jobs/{job_id}/download")
async def download_backup(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Download a backup file. Supports local and cloud storage backends."""
    orchestrator = BackupOrchestrator(db)
    job = await orchestrator.get_backup_job(job_id)
    
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Backup job '{job_id}' not found.")
    
    if job["status"] != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Cannot download backup with status '{job['status']}'. Only completed backups can be downloaded."
        )
    
    destination_path = job.get("destination_path")
    if not destination_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup destination path not found.")
    
    # Handle cloud downloads - download to temp file and stream
    if destination_path.startswith("gs://") or destination_path.startswith("b2://"):
        # Determine provider from tier
        tier = job.get("tier", "cloud_gcs")
        provider = "google_cloud_storage" if "gcs" in tier or destination_path.startswith("gs://") else "backblaze_b2"
        
        # Create temp file for download
        temp_filename = f"backup_{job_id}_{uuid.uuid4().hex}.zip"
        temp_path = Path(tempfile.gettempdir()) / temp_filename
        
        try:
            cloud_downloader = CloudDownloadService(provider)
            
            # Run synchronous download in thread pool
            loop = asyncio.get_event_loop()
            download_result = await loop.run_in_executor(
                None, 
                lambda: cloud_downloader.download(destination_path, str(temp_path))
            )
            
            if download_result.get("status") == "FAILED":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Cloud download failed: {download_result.get('error_message', 'Unknown error')}"
                )
            
            downloaded_path = Path(download_result.get("destination_path", str(temp_path)))
            final_path = download_result.get("decrypted_path", str(temp_path))
            downloaded_path = Path(final_path)
            
            # Determine filename from path
            filename = downloaded_path.name
            if downloaded_path.suffix == ".enc":
                filename = downloaded_path.stem + ".zip"
            
            return StreamingResponse(
                _stream_and_cleanup(downloaded_path),
                media_type="application/zip",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Failed to download backup {job_id} from cloud: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to download backup: {str(exc)}"
            )
    
    # Handle local downloads - stream directly from file
    else:
        local_path = Path(destination_path)
        if not local_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup file not found on storage.")
        
        return StreamingResponse(
            _stream_file(local_path),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{local_path.name}"'
            }
        )


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