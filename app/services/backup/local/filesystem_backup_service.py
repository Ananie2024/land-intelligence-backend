# app/services/backup/local/filesystem_backup_service.py
# app/services/backup/local/filesystem_backup_service.py
"""
Filesystem Backup Service
Land Intelligence System

Creates a ZIP archive of the application's file-storage directory
and enforces the local retention policy by pruning old archives.
"""

import logging
import shutil
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.backup_config import get_filesystem_backup_dir, RETENTION_POLICY, BackupTier
from app.utils.checksum_calculator import calculate_sha256

logger = logging.getLogger(__name__)


class FilesystemBackupService:
    """
    Archives the application file-storage directory as a ZIP.

    Archive is written to:
        <BACKUP_BASE_PATH>/filesystem/<job_id>/<job_id>.zip
    """

    def __init__(
        self,
        source_path: str | None = None,
        backup_dir: str | None = None,
        retention: int | None = None,
    ) -> None:
        self.source_path = Path(source_path or settings.FILE_STORAGE_PATH).resolve()
        self.backup_dir = Path(backup_dir).resolve() if backup_dir else get_filesystem_backup_dir()
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.retention = retention if retention is not None else RETENTION_POLICY[BackupTier.LOCAL]

    async def perform_backup(self, job_id: str) -> dict[str, Any]:
        destination_dir = self.backup_dir / job_id
        destination_dir.mkdir(parents=True, exist_ok=True)
        archive_path = destination_dir / f"{job_id}.zip"

        try:
            if not self.source_path.exists():
                raise FileNotFoundError(
                    f"File-storage source does not exist: {self.source_path}"
                )

            file_count, total_bytes = self._count_source(self.source_path)

            logger.info(
                "Archiving %d files (%d bytes) from %s → %s",
                file_count, total_bytes, self.source_path, archive_path,
            )

            shutil.make_archive(
                base_name=str(archive_path.with_suffix("")),
                format="zip",
                root_dir=str(self.source_path.parent),
                base_dir=self.source_path.name,
            )

            checksum = calculate_sha256(archive_path)
            size = archive_path.stat().st_size

            logger.info("Filesystem backup completed for job %s: %d bytes", job_id, size)

            self._prune_old_archives()

            return {
                "status": "COMPLETED",
                "destination_path": str(archive_path),
                "file_size_bytes": size,
                "file_count": file_count,
                "checksum": checksum,
            }

        except Exception as exc:
            logger.error("Filesystem backup failed for job %s: %s", job_id, exc, exc_info=True)
            return {"status": "FAILED", "error_message": str(exc)}

    @staticmethod
    def _count_source(source: Path) -> tuple[int, int]:
        count, total = 0, 0
        if source.is_file():
            return 1, source.stat().st_size
        for p in source.rglob("*"):
            if p.is_file():
                count += 1
                total += p.stat().st_size
        return count, total

    def _prune_old_archives(self) -> None:
        job_dirs = sorted(
            [d for d in self.backup_dir.iterdir() if d.is_dir()],
            key=lambda d: d.stat().st_ctime,
        )
        excess = len(job_dirs) - self.retention
        for old_dir in job_dirs[:excess]:
            try:
                shutil.rmtree(old_dir)
                logger.info("Pruned old filesystem backup: %s", old_dir)
            except Exception as exc:
                logger.warning("Could not prune %s: %s", old_dir, exc)