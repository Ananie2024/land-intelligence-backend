import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseRestoreService:
    def restore(self, backup_path: str, restore_job_id: str) -> dict:
        """
        Restore database from a SQL dump backup.
        """
        logger.info("Starting database restore from %s for job %s", backup_path, restore_job_id)

        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")

            db_params = urlparse(settings.DATABASE_URL)
            database = db_params.path.lstrip("/")
            if not database:
                database = "land_intelligence"

            hostname = db_params.hostname or "localhost"
            username = db_params.username or "root"
            password = db_params.password or ""

            cmd = [
                "psql",
                f"-h={hostname}",
                f"-U={username}",
                database,
            ]

            with open(backup_file, "r", encoding="utf-8") as f:
                result = subprocess.run(cmd, stdin=f, shell=False, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                raise RuntimeError(f"DB restore failed: {result.stderr}")

            logger.info("Database restore completed successfully for job %s", restore_job_id)
            return {
                "status": "COMPLETED",
                "restored_at": datetime.now(timezone.utc).isoformat(),
                "backup_path": str(backup_file),
                "restore_job_id": restore_job_id,
            }

        except Exception as exc:
            logger.error("Database restore failed for job %s: %s", restore_job_id, exc, exc_info=True)
            return {
                "status": "FAILED",
                "error_message": str(exc),
                "restored_at": datetime.now(timezone.utc).isoformat(),
            }
