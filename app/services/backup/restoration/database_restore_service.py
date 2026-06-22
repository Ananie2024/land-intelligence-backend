import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class DatabaseRestoreService:
    def restore(self, backup_path: str, restore_job_id: str) -> dict:
        logger.info("Simulating DB restore from %s for job %s", backup_path, restore_job_id)
        return {
            "status": "COMPLETED",
            "restored_at": datetime.now(timezone.utc).isoformat(),
        }
