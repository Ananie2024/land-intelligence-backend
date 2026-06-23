import logging
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings
from app.services.backup.cloud.google_cloud_storage_provider import GoogleCloudStorageProvider
from app.services.backup.cloud.backblaze_b2_provider import BackblazeB2Provider

logger = logging.getLogger(__name__)


class CloudDownloadService:
    def __init__(self, cloud_provider: str = "google_cloud_storage"):
        self.cloud_provider = cloud_provider
        if cloud_provider == "google_cloud_storage":
            self.provider = GoogleCloudStorageProvider()
        elif cloud_provider == "backblaze_b2":
            self.provider = BackblazeB2Provider()
        else:
            raise ValueError(f"Unsupported cloud provider: {cloud_provider}")

    def download(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """
        Download a backup from cloud storage to local destination.
        """
        logger.info(
            "Downloading from %s provider: %s -> %s",
            self.cloud_provider, source_path, destination_path
        )

        try:
            result = self.provider.download(source_path, destination_path)
            logger.info("Cloud download completed successfully")
            return result
        except Exception as exc:
            logger.error("Cloud download failed: %s", exc, exc_info=True)
            return {
                "status": "FAILED",
                "error_message": str(exc),
                "source_path": source_path,
                "destination_path": destination_path,
            }