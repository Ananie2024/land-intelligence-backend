import logging
import zipfile
from pathlib import Path

from app.models.backup_job import BackupJobStatus
from app.services.backup.validation.integrity_checker import IntegrityChecker

logger = logging.getLogger(__name__)


class BackupVerifier:
    def verify(self, backup_job) -> bool:
        logger.info("Verifying backup job %s", getattr(backup_job, "id", "unknown"))

        if getattr(backup_job, "status", None) != BackupJobStatus.COMPLETED.value:
            logger.warning("Backup not completed")
            return False

        destination = Path(getattr(backup_job, "destination_path", "") or "")
        if not destination.is_file():
            logger.warning("Missing destination path")
            return False

        if not zipfile.is_zipfile(destination):
            logger.warning("Backup destination is not a valid ZIP archive: %s", destination)
            return False

        return IntegrityChecker().check(backup_job)
