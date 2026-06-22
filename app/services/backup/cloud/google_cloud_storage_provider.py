import logging
from typing import Dict, Any
from app.services.backup.cloud.cloud_storage_interface import CloudStorageInterface

logger = logging.getLogger(__name__)


class GoogleCloudStorageProvider(CloudStorageInterface):
    def upload(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        logger.info("Simulating GCS upload %s -> %s", source_path, destination_path)
        return {"status": "COMPLETED", "destination_path": destination_path}

    def download(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        logger.info("Simulating GCS download %s -> %s", source_path, destination_path)
        return {"status": "COMPLETED", "destination_path": destination_path}
