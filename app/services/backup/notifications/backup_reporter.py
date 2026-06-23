import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class BackupReporter:
    def report(self, backup_job: Any) -> str:
        """
        Generate a human-readable report for a backup/restore job.
        """
        job_id = getattr(backup_job, "id", "unknown")
        status = getattr(backup_job, "status", "UNKNOWN")
        job_type = getattr(backup_job, "job_type", "BACKUP")
        completed_at = getattr(backup_job, "completed_at", None)

        report = f"""
Backup/restore Job Report
=========================
Job ID          : {job_id}
Type            : {job_type}
Status          : {status}
Started         : {getattr(backup_job, 'created_at', 'N/A')}
Completed       : {completed_at or datetime.now(timezone.utc).isoformat()}
Destination     : {getattr(backup_job, 'destination_path', 'N/A')}
Error           : {getattr(backup_job, 'error_message', 'None')}
        """.strip()

        logger.info("Generated report for job %s", job_id)
        return report