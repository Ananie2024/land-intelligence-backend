# app/services/backup/local/config_backup_service.py
"""
Config Backup Service
Land Intelligence System

Backs up YAML configuration files and the .env file to a ZIP archive.
"""

import logging
import zipfile
from pathlib import Path
from typing import Any

from app.core.backup_config import get_config_backup_dir
from app.utils.checksum_calculator import calculate_sha256

logger = logging.getLogger(__name__)

_CONFIG_GLOBS: list[tuple[str, str]] = [
    ("config", "**/*.yaml"),
    ("config", "**/*.yml"),
    (".", ".env"),
    (".", "alembic.ini"),
    (".", "requirements.txt"),
    (".", "constraints.txt"),
]

# app/services/backup/local/ → parents[3] = app/ → parents[4] = project root
_PROJECT_ROOT = Path(__file__).resolve().parents[4]


class ConfigBackupService:
    """
    Collects YAML configs, .env, and dependency manifests into a ZIP archive.

    Archive is written to:
        <BACKUP_BASE_PATH>/config/<job_id>/<job_id>-config.zip
    """

    def __init__(self, backup_dir: str | None = None) -> None:
        self.backup_dir = Path(backup_dir).resolve() if backup_dir else get_config_backup_dir()
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    async def perform_backup(self, job_id: str) -> dict[str, Any]:
        destination_dir = self.backup_dir / job_id
        destination_dir.mkdir(parents=True, exist_ok=True)
        archive_path = destination_dir / f"{job_id}-config.zip"

        try:
            files = self._collect_files()
            if not files:
                logger.warning("No configuration files found to back up for job %s.", job_id)

            self._write_archive(files, archive_path)

            size = archive_path.stat().st_size
            checksum = calculate_sha256(archive_path)

            logger.info(
                "Config backup completed for job %s: %d files, %d bytes",
                job_id, len(files), size,
            )
            return {
                "status": "COMPLETED",
                "destination_path": str(archive_path),
                "file_size_bytes": size,
                "file_count": len(files),
                "checksum": checksum,
            }

        except Exception as exc:
            logger.error("Config backup failed for job %s: %s", job_id, exc, exc_info=True)
            return {"status": "FAILED", "error_message": str(exc)}

    def _collect_files(self) -> list[tuple[Path, str]]:
        collected: list[tuple[Path, str]] = []
        root = _PROJECT_ROOT

        for base, pattern in _CONFIG_GLOBS:
            search_root = (root / base).resolve()
            if not search_root.exists():
                continue
            if "*" in pattern:
                for match in search_root.glob(pattern):
                    if match.is_file():
                        collected.append((match, str(match.relative_to(root))))
            else:
                candidate = (root / pattern).resolve() if base == "." else (root / base / pattern).resolve()
                if candidate.is_file():
                    collected.append((candidate, str(candidate.relative_to(root))))

        seen: set[str] = set()
        unique: list[tuple[Path, str]] = []
        for abs_path, arc in collected:
            if arc not in seen:
                seen.add(arc)
                unique.append((abs_path, arc))
        return unique

    @staticmethod
    def _write_archive(files: list[tuple[Path, str]], archive_path: Path) -> None:
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for abs_path, arc_name in files:
                zf.write(abs_path, arcname=arc_name)