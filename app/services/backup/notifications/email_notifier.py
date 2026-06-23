import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Service for sending email notifications about backup/restore jobs.
    Uses SMTP configuration from settings.
    """

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.sender_email = settings.EMAIL_SENDER or self.smtp_user
        self.default_recipients = settings.BACKUP_NOTIFICATION_EMAILS or []

    def send_backup_notification(
        self,
        job: Any,
        recipients: Optional[list] = None,
        include_report: bool = True
    ) -> Dict[str, Any]:
        """
        Send email notification for a backup or restore job.
        """
        if not recipients:
            recipients = self.default_recipients

        if not recipients:
            logger.warning("No recipients configured for backup notification")
            return {"status": "SKIPPED", "reason": "No recipients"}

        try:
            report = ""
            if include_report:
                from .backup_reporter import BackupReporter
                reporter = BackupReporter()
                report = reporter.report(job)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Land Intelligence Backup - {getattr(job, 'job_type', 'JOB')} {getattr(job, 'status', 'UNKNOWN')}"
            msg["From"] = self.sender_email
            msg["To"] = ", ".join(recipients)

            html_content = f"""
            <html>
            <body>
                <h2>Backup Job Update</h2>
                <pre style="background:#f4f4f4;padding:15px;border-radius:5px;">{report}</pre>
                <p>This is an automated notification from the Land Intelligence System.</p>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_content, "html"))

            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.sender_email, recipients, msg.as_string())

            logger.info("Backup notification email sent successfully to %s", recipients)
            return {
                "status": "SENT",
                "recipients": recipients,
                "job_id": getattr(job, "id", None)
            }

        except Exception as exc:
            logger.error("Failed to send backup notification email: %s", exc, exc_info=True)
            return {
                "status": "FAILED",
                "error_message": str(exc)
            }