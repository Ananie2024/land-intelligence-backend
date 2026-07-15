# app/api/v1/routes/settings.py
"""
Settings API Routes
Land Intelligence System
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.config import settings as app_settings
from app.api.auth_dependencies import get_current_user_id, require_admin

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    summary="Get system settings",
    description="Return the current application settings (non-sensitive fields only).",
)
async def get_settings(
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Return a safe subset of the current system settings."""
    return {
        "api_url": f"http://{app_settings.API_HOST}:{app_settings.API_PORT}",
        "app_url": f"http://{app_settings.API_HOST}:{app_settings.API_PORT}",
        "debug_mode": app_settings.ENVIRONMENT != "production",
        "log_level": app_settings.LOG_LEVEL,
        "max_upload_size_mb": app_settings.MAX_UPLOAD_SIZE_MB,
        "allowed_extensions": app_settings.ALLOWED_EXTENSIONS,
        "backup_base_path": app_settings.BACKUP_BASE_PATH,
        "file_storage_path": app_settings.FILE_STORAGE_PATH,
    }


@router.patch(
    "",
    summary="Update system settings",
    description="Update writable application settings (PATCH semantics for partial updates).",
)
async def update_settings(
    payload: dict[str, Any],
    user_id: str = Depends(get_current_user_id),
    _admin: str = Depends(require_admin),
) -> dict[str, Any]:
    """Update application settings. Accepts a partial JSON body of writable fields."""
    # Currently a no-op for security; returns the current safe settings.
    # In a production deployment this would persist to a database or config file.
    logger.info(f"Settings update requested by user {user_id}: {list(payload.keys())}")
    from app.core.config import settings as app_settings
    return {
        "api_url": f"http://{app_settings.API_HOST}:{app_settings.API_PORT}",
        "app_url": f"http://{app_settings.API_HOST}:{app_settings.API_PORT}",
        "debug_mode": app_settings.ENVIRONMENT != "production",
        "log_level": app_settings.LOG_LEVEL,
        "max_upload_size_mb": app_settings.MAX_UPLOAD_SIZE_MB,
        "allowed_extensions": app_settings.ALLOWED_EXTENSIONS,
        "backup_base_path": app_settings.BACKUP_BASE_PATH,
        "file_storage_path": app_settings.FILE_STORAGE_PATH,
    }


@router.get(
    "/logs",
    summary="Get system logs",
    description="Return the most recent log entries from the application log file.",
)
async def get_system_logs(
    limit: int = Query(10, ge=1, le=500, description="Number of log entries to return"),
    level: Optional[str] = Query(None, description="Filter by log level (e.g. INFO, WARNING, ERROR)"),
    user_id: str = Depends(get_current_user_id),
    _admin: str = Depends(require_admin),
) -> list[dict[str, Any]]:
    """Read the last N log entries from the application log file."""
    log_file_path = Path(app_settings.LOG_FILE_PATH)

    if not log_file_path.exists():
        return []

    try:
        entries: list[dict[str, Any]] = []
        # Read the file in reverse to get the most recent entries first
        with open(log_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Parse each line as JSON and collect valid entries
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                entry: dict[str, Any] = json.loads(line)
            except json.JSONDecodeError:
                # Skip non-JSON lines
                continue

            # Apply optional level filter
            if level and entry.get("level", "").upper() != level.upper():
                continue

            entries.append(entry)
            if len(entries) >= limit:
                break

        return entries
    except Exception as exc:
        logger.error(f"Failed to read log file: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read log file: {str(exc)}",
        )
