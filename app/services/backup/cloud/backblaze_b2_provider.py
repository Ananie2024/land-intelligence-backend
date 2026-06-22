import logging
from typing import Dict, Any
from app.services.backup.cloud.cloud_storage_interface import CloudStorageInterface

logger = logging.getLogger(__name__)


class BackblazeB2Provider(CloudStorageInterface):
    def upload(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        logger.info("Simulating B2 upload %s -> %s", source_path, destination_path)
        return {"status": "COMPLETED", "destination_path": destination_path}

    def download(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        logger.info("Simulating B2 download %s -> %s", source_path, destination_path)
        return {"status": "COMPLETED", "destination_path": destination_path}
