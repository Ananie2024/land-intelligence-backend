import logging
import os
import shutil

logger = logging.getLogger(__name__)


class FileSystemRestoreService:
    def __init__(self, base_restore_path: str = "backups/restore/") -> None:
        self.base_restore_path = base_restore_path
        os.makedirs(base_restore_path, exist_ok=True)

    def restore(self, source_path: str, restore_job_id: str) -> dict:
        destination_path = os.path.join(self.base_restore_path, restore_job_id)
        os.makedirs(destination_path, exist_ok=True)
        try:
            if os.path.isdir(source_path):
                dest = os.path.join(destination_path, os.path.basename(source_path))
                shutil.copytree(source_path, dest, dirs_exist_ok=True)
            elif os.path.isfile(source_path):
                shutil.copy(source_path, os.path.join(destination_path, os.path.basename(source_path)))
            else:
                raise FileNotFoundError("Source path not found")
            logger.info("FileSystem restore completed for job %s", restore_job_id)
            return {"status": "COMPLETED", "destination_path": destination_path}
        except Exception as exc:
            logger.error("FileSystem restore failed for job %s: %s", restore_job_id, exc)
            return {"status": "FAILED", "error_message": str(exc)}
