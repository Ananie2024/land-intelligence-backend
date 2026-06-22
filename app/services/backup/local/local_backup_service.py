import json
import logging
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.utils.checksum_calculator import calculate_sha256

logger = logging.getLogger(__name__)


class LocalBackupService:
    def __init__(self, base_backup_path: str | None = None):
        self.base_backup_path = Path(base_backup_path or settings.BACKUP_BASE_PATH).resolve()
        self.base_backup_path.mkdir(parents=True, exist_ok=True)

    async def perform_backup(self, source_path: str | None, job_id: str) -> dict[str, Any]:
        source = Path(source_path or settings.FILE_STORAGE_PATH).resolve()
        destination_dir = (self.base_backup_path / "daily" / job_id).resolve()

        try:
            if not source.exists():
                raise FileNotFoundError(f"Source path does not exist: {source}")

            destination_dir.mkdir(parents=True, exist_ok=True)
            archive_path = destination_dir / f"{job_id}.zip"
            manifest_path = destination_dir / f"{job_id}.manifest.json"

            manifest = self._build_manifest(source)
            self._write_archive(source, archive_path)

            archive_checksum = calculate_sha256(archive_path)
            manifest_payload = {
                "job_id": job_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source_path": str(source),
                "archive_path": str(archive_path),
                "archive_checksum_sha256": archive_checksum,
                "file_count": manifest["file_count"],
                "file_size_bytes": manifest["file_size_bytes"],
                "files": manifest["files"],
            }
            manifest_path.write_text(
                json.dumps(manifest_payload, indent=2, sort_keys=True),
                encoding="utf-8",
            )

            logger.info(
                "Local backup completed for %s: %s files, %s bytes -> %s",
                source,
                manifest["file_count"],
                manifest["file_size_bytes"],
                archive_path,
            )
            return {
                "status": "COMPLETED",
                "file_size_bytes": manifest["file_size_bytes"],
                "file_count": manifest["file_count"],
                "destination_path": str(archive_path),
                "manifest_path": str(manifest_path),
                "checksum": archive_checksum,
            }
        except Exception as exc:
            logger.error("Local backup failed for %s: %s", source, exc, exc_info=True)
            return {
                "status": "FAILED",
                "error_message": str(exc),
            }

    def _iter_source_files(self, source: Path) -> list[Path]:
        if source.is_file():
            return [source]

        files: list[Path] = []
        for path in source.rglob("*"):
            if path.is_file():
                files.append(path)
        return sorted(files, key=lambda p: str(p.relative_to(source)).lower())

    def _archive_name(self, source: Path, file_path: Path) -> str:
        if source.is_file():
            return source.name
        return str(file_path.relative_to(source)).replace(os.sep, "/")

    def _build_manifest(self, source: Path) -> dict[str, Any]:
        files = []
        total_size = 0

        for file_path in self._iter_source_files(source):
            size = file_path.stat().st_size
            total_size += size
            files.append(
                {
                    "path": self._archive_name(source, file_path),
                    "source_path": str(file_path),
                    "size_bytes": size,
                    "checksum_sha256": calculate_sha256(file_path),
                }
            )

        return {
            "file_count": len(files),
            "file_size_bytes": total_size,
            "files": files,
        }

    def _write_archive(self, source: Path, archive_path: Path) -> None:
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in self._iter_source_files(source):
                zip_file.write(file_path, arcname=self._archive_name(source, file_path))
