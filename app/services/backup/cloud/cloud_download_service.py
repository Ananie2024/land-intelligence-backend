import logging
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings
from app.services.backup.cloud.encryption_service import EncryptionService
from app.services.backup.cloud.google_cloud_storage_provider import GoogleCloudStorageProvider
from app.services.backup.cloud.backblaze_b2_provider import BackblazeB2Provider

logger = logging.getLogger(__name__)


class CloudDownloadService:
    def __init__(self, cloud_provider: str = "google_cloud_storage"):
        self.cloud_provider = cloud_provider
        if cloud_provider == "google_cloud_storage":
            self.provider = GoogleCloudStorageProvider()
            self.encryption_enabled = settings.GCS_ENCRYPTION_ENABLED
            self.encryption_service = EncryptionService() if self.encryption_enabled else None
        elif cloud_provider == "backblaze_b2":
            self.provider = BackblazeB2Provider()
            self.encryption_enabled = getattr(settings, 'B2_ENCRYPTION_ENABLED', False)
            self.encryption_service = EncryptionService() if self.encryption_enabled else None
        else:
            raise ValueError(f"Unsupported cloud provider: {cloud_provider}")

    def download(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """
        Download a backup from cloud storage to local destination.
        Decrypt the file if it was encrypted during backup.
        """
        logger.info(
            "Downloading from %s provider: %s -> %s",
            self.cloud_provider, source_path, destination_path
        )

        try:
            result = self.provider.download(source_path, destination_path)
            
            # Decrypt if enabled and file is encrypted
            if self.encryption_service and Path(destination_path).exists():
                downloaded_file = result.get("destination_path", destination_path)
                if Path(downloaded_file).suffix == ".enc":
                    logger.info("Decrypting downloaded backup file")
                    decrypt_result = self.encryption_service.decrypt(downloaded_file)
                    if decrypt_result.get("status") == "FAILED":
                        return {
                            "status": "FAILED",
                            "error_message": f"Decryption failed: {decrypt_result.get('error_message')}",
                            "source_path": source_path,
                            "destination_path": downloaded_file,
                        }
                    result["decrypted_path"] = decrypt_result.get("decrypted_path")
                    result["encrypted"] = True
            
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