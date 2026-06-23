# app/services/backup/notifications/failure_alerter.py
# app/services/backup/notifications/failure_alerter.py
"""
Failure Alerter
Land Intelligence System

Sends an alert notification when a backup job fails.
"""

import logging
from typing import Any

from app.services.backup.notifications.email_notifier import EmailNotifier
from app.services.backup.notifications.backup_reporter import BackupReporter

logger = logging.getLogger(__name__)

_DEFAULT_RECIPIENT = "admin@land-intelligence.local"


class FailureAlerter:

    def __init__(
        self,
        notifier: EmailNotifier | None = None,
        reporter: BackupReporter | None = None,
    ) -> None:
        self.notifier = notifier or EmailNotifier()
        self.reporter = reporter or BackupReporter()

    def alert(self, backup_job: Any, recipient: str = _DEFAULT_RECIPIENT) -> None:
        job_id = getattr(backup_job, "id", "unknown")
        job_type = getattr(backup_job, "job_type", "unknown")
        tier = getattr(backup_job, "tier", "unknown")
        error = getattr(backup_job, "error_message", "No error message recorded.")

        subject = f"[ALERT] Backup job {job_id} FAILED — type={job_type}, tier={tier}"
        body = (
            f"A backup job has failed and requires attention.\n\n"
            f"Job ID    : {job_id}\n"
            f"Type      : {job_type}\n"
            f"Tier      : {tier}\n"
            f"Error     : {error}\n\n"
            f"--- Backup Report ---\n"
            f"{self.reporter.report(backup_job)}\n\n"
            f"Please investigate the backup system immediately.\n"
        )

        logger.warning(
            "FailureAlerter: dispatching failure alert for job %s to %s", job_id, recipient
        )
        self.notifier.send(recipient=recipient, subject=subject, body=body)