import logging
from app.models.backup_job import BackupJobStatus

logger = logging.getLogger(__name__)


class BackupVerifier:
    def verify(self, backup_job) -> bool:
        logger.info("Verifying backup job %s", getattr(backup_job, "id", "unknown"))
        if getattr(backup_job, "status", None) != BackupJobStatus.COMPLETED.value:
            logger.warning("Backup not completed")
            return False
        if not getattr(backup_job, "destination_path", None):
            logger.warning("Missing destination path")
            return False
        return True
