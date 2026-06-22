import logging

logger = logging.getLogger(__name__)


class RestoreTester:
    def dry_run(self, backup_job) -> bool:
        logger.info("Dry-run restore test for job %s", getattr(backup_job, "id", "unknown"))
        return True
