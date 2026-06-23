# app/services/backup/local/local_backup_manager.py
# app/services/backup/local/local_backup_manager.py
"""
Local Backup Manager
Land Intelligence System

Coordinates the full local backup pass (3-2-1 local tier):
  1. Database dump
  2. File-storage archive
  3. Configuration archive

All three run concurrently via asyncio.gather.
"""

import asyncio
import logging
from typing import Any

from app.services.backup.local.database_backup_service import DatabaseBackupService
from app.services.backup.local.filesystem_backup_service import FilesystemBackupService
from app.services.backup.local.config_backup_service import ConfigBackupService

logger = logging.getLogger(__name__)


class LocalBackupManager:

    def __init__(self) -> None:
        self.db_service = DatabaseBackupService()
        self.fs_service = FilesystemBackupService()
        self.cfg_service = ConfigBackupService()

    async def run_full_backup(self, job_id: str) -> dict[str, Any]:
        logger.info("LocalBackupManager: starting full backup for job %s", job_id)

        db_result, fs_result, cfg_result = await asyncio.gather(
            self.db_service.perform_backup(job_id),
            self.fs_service.perform_backup(job_id),
            self.cfg_service.perform_backup(job_id),
        )

        components = {
            "database": db_result,
            "filesystem": fs_result,
            "config": cfg_result,
        }

        failed = [name for name, r in components.items() if r.get("status") != "COMPLETED"]

        if failed:
            errors = "; ".join(
                f"{name}: {components[name].get('error_message', 'unknown')}"
                for name in failed
            )
            logger.error("LocalBackupManager: job %s partial failure — %s", job_id, errors)
            return {
                "status": "FAILED",
                "error_message": errors,
                "components": components,
                "file_size_bytes": self._total(components, "file_size_bytes"),
                "file_count": self._total(components, "file_count"),
            }

        total_bytes = self._total(components, "file_size_bytes")
        total_files = self._total(components, "file_count")
        destination = fs_result.get("destination_path") or db_result.get("destination_path", "")
        checksum = fs_result.get("checksum") or db_result.get("checksum", "")

        logger.info(
            "LocalBackupManager: job %s completed — %d files, %d bytes",
            job_id, total_files, total_bytes,
        )
        return {
            "status": "COMPLETED",
            "destination_path": destination,
            "checksum": checksum,
            "file_size_bytes": total_bytes,
            "file_count": total_files,
            "components": components,
        }

    async def run_database_backup(self, job_id: str) -> dict[str, Any]:
        return await self.db_service.perform_backup(job_id)

    async def run_filesystem_backup(self, job_id: str) -> dict[str, Any]:
        return await self.fs_service.perform_backup(job_id)

    async def run_config_backup(self, job_id: str) -> dict[str, Any]:
        return await self.cfg_service.perform_backup(job_id)

    @staticmethod
    def _total(components: dict[str, dict[str, Any]], key: str) -> int:
        return sum(int(r.get(key) or 0) for r in components.values())