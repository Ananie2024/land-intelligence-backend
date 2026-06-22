import logging
from app.models.backup_job import BackupJobStatus

logger = logging.getLogger(__name__)


class IntegrityChecker:
    def check(self, backup_job) -> bool:
        logger.info("Checking integrity for backup job %s", getattr(backup_job, "id", "unknown"))
        if getattr(backup_job, "status", None) != BackupJobStatus.COMPLETED.value:
            logger.warning("Backup not completed")
            return False
        return True
