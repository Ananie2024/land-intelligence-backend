import logging
import os

from app.models.backup_job import BackupJobStatus

logger = logging.getLogger(__name__)


class RestoreValidator:
    def validate(self, backup) -> bool:
        logger.info("Validating backup %s", getattr(backup, "id", "unknown"))
        if getattr(backup, "status", None) != BackupJobStatus.COMPLETED.value:
            logger.warning("Backup not completed")
            return False
        if not getattr(backup, "destination_path", None):
            logger.warning("Backup missing destination_path")
            return False
        return True
