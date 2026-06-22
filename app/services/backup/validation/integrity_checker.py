import logging
from pathlib import Path

from app.models.backup_job import BackupJobStatus
from app.utils.checksum_calculator import calculate_sha256

logger = logging.getLogger(__name__)


class IntegrityChecker:
    def check(self, backup_job) -> bool:
        logger.info("Checking integrity for backup job %s", getattr(backup_job, "id", "unknown"))

        if getattr(backup_job, "status", None) != BackupJobStatus.COMPLETED.value:
            logger.warning("Backup not completed")
            return False

        destination = Path(getattr(backup_job, "destination_path", "") or "")
        if not destination.is_file():
            logger.warning("Backup destination does not exist: %s", destination)
            return False

        expected_checksum = getattr(backup_job, "checksum", None)
        if expected_checksum and calculate_sha256(destination) != expected_checksum:
            logger.warning("Backup archive checksum mismatch")
            return False

        return True
