import logging
import shutil
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)


class LocalBackupService:
    def __init__(self, base_backup_path: str = "backups/"):
        self.base_backup_path = base_backup_path
        os.makedirs(base_backup_path, exist_ok=True)

    async def perform_backup(self, source_path: str, job_id: str) -> Dict[str, Any]:
        destination_path = os.path.join(self.base_backup_path, "daily", job_id)
        os.makedirs(destination_path, exist_ok=True)
        
        try:
            if os.path.isdir(source_path):
                shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
                logger.info(f"Successfully backed up directory {source_path} to {destination_path}")
            elif os.path.isfile(source_path):
                shutil.copy(source_path, destination_path)
                logger.info(f"Successfully backed up file {source_path} to {destination_path}")
            else:
                raise FileNotFoundError(f"Source path {source_path} does not exist or is not a file/directory.")

            # For simplicity, we\'ll return some basic info. 
            # In a real scenario, you\'d calculate actual file size, count, checksums.
            total_size = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, fn in os.walk(destination_path) for f in fn) 
            total_files = sum(len(fn) for dp, dn, fn in os.walk(destination_path))

            return {
                "status": "COMPLETED",
                "file_size_bytes": total_size,
                "file_count": total_files,
                "destination_path": destination_path,
                "checksum": "mock_checksum"
            }
        except Exception as e:
            logger.error(f"Local backup failed for {source_path}: {e}")
            return {
                "status": "FAILED",
                "error_message": str(e)
            }
