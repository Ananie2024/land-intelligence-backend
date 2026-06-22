import logging
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.backup.cloud.backblaze_b2_provider import BackblazeB2Provider
from app.services.backup.cloud.google_cloud_storage_provider import GoogleCloudStorageProvider
from app.services.backup.local.local_backup_service import LocalBackupService

logger = logging.getLogger(__name__)


class CloudBackupService:
    def __init__(self, cloud_provider: str):
        self.cloud_provider = cloud_provider
        self.staging_backup_service = LocalBackupService(
            str(Path(settings.BACKUP_BASE_PATH) / "cloud_staging" / cloud_provider)
        )

        if cloud_provider == "google_cloud_storage":
            self.provider = GoogleCloudStorageProvider()
        elif cloud_provider == "backblaze_b2":
            self.provider = BackblazeB2Provider()
        else:
            raise ValueError(f"Unsupported cloud provider: {cloud_provider}")

    async def perform_backup(self, source_path: str | None, job_id: str) -> dict[str, Any]:
        logger.info(
            "Preparing cloud backup for provider %s, job %s, source %s",
            self.cloud_provider,
            job_id,
            source_path or settings.FILE_STORAGE_PATH,
        )

        local_result = await self.staging_backup_service.perform_backup(source_path, job_id)
        if local_result.get("status") != "COMPLETED":
            return local_result

        archive_path = local_result["destination_path"]
        destination_key = f"daily/{job_id}/{Path(archive_path).name}"

        try:
            upload_result = self.provider.upload(archive_path, destination_key)
            return {
                "status": upload_result.get("status", "COMPLETED"),
                "file_size_bytes": local_result.get("file_size_bytes"),
                "file_count": local_result.get("file_count"),
                "destination_path": upload_result.get("destination_path"),
                "checksum": local_result.get("checksum"),
            }
        except Exception as exc:
            logger.error(
                "Cloud backup upload failed for provider %s and job %s: %s",
                self.cloud_provider,
                job_id,
                exc,
                exc_info=True,
            )
            return {
                "status": "FAILED",
                "error_message": str(exc),
                "destination_path": archive_path,
                "checksum": local_result.get("checksum"),
                "file_size_bytes": local_result.get("file_size_bytes"),
                "file_count": local_result.get("file_count"),
            }
