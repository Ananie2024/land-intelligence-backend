# app/services/backup/restoration/database_restore_service.py
"""
Database Restore Service
Land Intelligence System

Restores a PostgreSQL database from a plain-SQL dump produced by pg_dump.
Supports both uncompressed .sql files and gzip-compressed .sql.gz archives.

Security notes
--------------
* shell=False — no shell injection risk; backup_path is validated as a
  filesystem path before use.
* The database password is passed via the PGPASSWORD environment variable,
  not as a CLI argument, so it never appears in process listings.
* psql flags use the two-element form ("-h", value) rather than "-h=value",
  which is unsupported by psql and was the previous bug.
"""

import gzip
import logging
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseRestoreService:

    def restore(self, backup_path: str, restore_job_id: str) -> dict:
        """
        Restore the database from a SQL dump.

        Args:
            backup_path:     Absolute path to a .sql or .sql.gz backup file.
            restore_job_id:  Identifier used only for log correlation.

        Returns:
            dict with keys: status, restored_at, backup_path, restore_job_id
            On failure: status="FAILED", error_message=<reason>
        """
        logger.info(
            "Starting database restore from %s for job %s",
            backup_path,
            restore_job_id,
        )

        tmp_sql: str | None = None  # track any temp file we create

        try:
            backup_file = Path(backup_path).resolve()
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")

            # ----------------------------------------------------------
            # Decompress if necessary
            # ----------------------------------------------------------
            sql_file: Path
            if backup_file.suffix == ".gz":
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=".sql")
                os.close(tmp_fd)
                tmp_sql = tmp_path
                logger.info("Decompressing %s → %s", backup_file, tmp_path)
                with gzip.open(backup_file, "rb") as gz_in, open(tmp_path, "wb") as out:
                    shutil.copyfileobj(gz_in, out)
                sql_file = Path(tmp_path)
            else:
                sql_file = backup_file

            # ----------------------------------------------------------
            # Parse connection parameters from the settings DSN
            # ----------------------------------------------------------
            parsed = urlparse(settings.DATABASE_URL)
            hostname = parsed.hostname or "localhost"
            port     = str(parsed.port or 5432)
            username = parsed.username or "land_user"
            password = parsed.password or ""
            database = parsed.path.lstrip("/") or "land_intelligence_db"

            # ----------------------------------------------------------
            # Build the psql command
            # Two-element flag form is required; "-h=value" is not valid
            # psql syntax and silently fails or prompts interactively.
            # ----------------------------------------------------------
            cmd = [
                "psql",
                "-h", hostname,
                "-p", port,
                "-U", username,
                "-d", database,
                "-v", "ON_ERROR_STOP=1",  # abort on first SQL error
            ]

            # Pass password through the environment — never as a CLI arg
            env = os.environ.copy()
            if password:
                env["PGPASSWORD"] = password

            logger.info("Executing psql restore for job %s", restore_job_id)

            with open(sql_file, "r", encoding="utf-8") as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    shell=False,          # no shell injection risk
                    capture_output=True,
                    text=True,
                    timeout=300,
                    env=env,
                )

            if result.returncode != 0:
                raise RuntimeError(
                    f"psql exited with code {result.returncode}: {result.stderr}"
                )

            logger.info(
                "Database restore completed successfully for job %s", restore_job_id
            )
            return {
                "status": "COMPLETED",
                "restored_at": datetime.now(timezone.utc).isoformat(),
                "backup_path": str(backup_file),
                "restore_job_id": restore_job_id,
            }

        except Exception as exc:
            logger.error(
                "Database restore failed for job %s: %s",
                restore_job_id,
                exc,
                exc_info=True,
            )
            return {
                "status": "FAILED",
                "error_message": str(exc),
                "restored_at": datetime.now(timezone.utc).isoformat(),
            }

        finally:
            # Clean up temporary decompressed file if we created one
            if tmp_sql and Path(tmp_sql).exists():
                try:
                    Path(tmp_sql).unlink()
                except OSError:
                    pass