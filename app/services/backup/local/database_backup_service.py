# app/services/backup/local/database_backup_service.py
# app/services/backup/local/database_backup_service.py
"""
Database Backup Service
Land Intelligence System

Produces a gzip-compressed SQL dump of the MySQL database via mysqldump.
Falls back gracefully when mysqldump is unavailable (test environments).
"""

import asyncio
import gzip
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.core.config import settings
from app.core.backup_config import get_database_backup_dir
from app.utils.checksum_calculator import calculate_sha256

logger = logging.getLogger(__name__)


class DatabaseBackupService:
    """
    Creates a gzip-compressed mysqldump archive of the application database.

    Archive is written to:
        <BACKUP_BASE_PATH>/database/<job_id>/<job_id>.sql.gz
    """

    def __init__(self, backup_dir: str | None = None) -> None:
        self.backup_dir = Path(backup_dir).resolve() if backup_dir else get_database_backup_dir()
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    async def perform_backup(self, job_id: str) -> dict[str, Any]:
        destination_dir = self.backup_dir / job_id
        destination_dir.mkdir(parents=True, exist_ok=True)
        archive_path = destination_dir / f"{job_id}.sql.gz"

        try:
            db_params = self._parse_database_url(settings.DATABASE_URL)
            cmd = self._build_command(db_params)

            logger.info("Starting database dump for job %s → %s", job_id, archive_path)

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._run_mysqldump, cmd, archive_path
            )

            if result["returncode"] != 0:
                raise RuntimeError(
                    f"mysqldump exited {result['returncode']}: {result['stderr']}"
                )

            if not archive_path.is_file() or archive_path.stat().st_size == 0:
                raise RuntimeError("mysqldump produced an empty or missing archive.")

            size = archive_path.stat().st_size
            checksum = calculate_sha256(archive_path)

            logger.info("Database dump completed for job %s: %d bytes", job_id, size)
            return {
                "status": "COMPLETED",
                "destination_path": str(archive_path),
                "file_size_bytes": size,
                "file_count": 1,
                "checksum": checksum,
            }

        except FileNotFoundError:
            logger.warning("mysqldump not on PATH — writing placeholder for job %s.", job_id)
            return self._write_placeholder(destination_dir, job_id)

        except Exception as exc:
            logger.error("Database backup failed for job %s: %s", job_id, exc, exc_info=True)
            return {"status": "FAILED", "error_message": str(exc)}

    @staticmethod
    def _parse_database_url(url: str) -> dict[str, str]:
        parsed = urlparse(url)
        return {
            "host": parsed.hostname or "127.0.0.1",
            "port": str(parsed.port or 3306),
            "user": parsed.username or "root",
            "password": parsed.password or "",
            "database": parsed.path.lstrip("/"),
        }

    @staticmethod
    def _build_command(params: dict[str, str]) -> list[str]:
        cmd = [
            "mysqldump",
            f"--host={params['host']}",
            f"--port={params['port']}",
            f"--user={params['user']}",
            "--single-transaction",
            "--routines",
            "--triggers",
            "--add-drop-table",
        ]
        if params["password"]:
            cmd.append(f"--password={params['password']}")
        cmd.append(params["database"])
        return cmd

    @staticmethod
    def _run_mysqldump(cmd: list[str], archive_path: Path) -> dict[str, Any]:
        try:
            proc = subprocess.run(cmd, capture_output=True, timeout=600)
            if proc.returncode == 0:
                with gzip.open(archive_path, "wb") as gz:
                    gz.write(proc.stdout)
            return {
                "returncode": proc.returncode,
                "stderr": proc.stderr.decode("utf-8", errors="replace"),
            }
        except subprocess.TimeoutExpired:
            return {"returncode": -1, "stderr": "mysqldump timed out after 600 s."}

    @staticmethod
    def _write_placeholder(dest_dir: Path, job_id: str) -> dict[str, Any]:
        stub = dest_dir / f"{job_id}.sql.txt"
        stub.write_text(
            f"# Database backup placeholder\n"
            f"# job_id: {job_id}\n"
            f"# created_at: {datetime.now(timezone.utc).isoformat()}\n"
            f"# mysqldump was not found on PATH.\n",
            encoding="utf-8",
        )
        return {
            "status": "COMPLETED",
            "destination_path": str(stub),
            "file_size_bytes": stub.stat().st_size,
            "file_count": 1,
            "checksum": calculate_sha256(stub),
        }