import logging

logger = logging.getLogger(__name__)


class BackupReporter:
    def report(self, backup_job) -> str:
        logger.info("Generating report for backup job %s", getattr(backup_job, "id", "unknown"))
        return f"Backup job report: {getattr(backup_job, 'id', 'unknown')}"
