import logging
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.backup.cloud.cloud_storage_interface import CloudStorageInterface

logger = logging.getLogger(__name__)


class BackblazeB2Provider(CloudStorageInterface):
    def upload(self, source_path: str, destination_path: str) -> dict[str, Any]:
        if not settings.B2_ENABLED:
            raise RuntimeError("Backblaze B2 backups are disabled.")
        if not settings.B2_ACCOUNT_ID or not settings.B2_APPLICATION_KEY or not settings.B2_BUCKET_NAME:
            raise RuntimeError("B2_ACCOUNT_ID, B2_APPLICATION_KEY, and B2_BUCKET_NAME are required.")

        source = Path(source_path)
        if not source.is_file():
            raise FileNotFoundError(f"Upload source file not found: {source}")

        try:
            from b2sdk.v2 import B2Api, InMemoryAccountInfo
        except ImportError as exc:
            raise RuntimeError("b2sdk is not installed.") from exc

        b2_api = B2Api(InMemoryAccountInfo())
        b2_api.authorize_account(
            "production",
            settings.B2_ACCOUNT_ID,
            settings.B2_APPLICATION_KEY,
        )
        bucket = b2_api.get_bucket_by_name(settings.B2_BUCKET_NAME)
        bucket.upload_local_file(
            local_file=str(source),
            file_name=destination_path,
        )

        logger.info("Uploaded %s to b2://%s/%s", source, settings.B2_BUCKET_NAME, destination_path)
        return {
            "status": "COMPLETED",
            "destination_path": f"b2://{settings.B2_BUCKET_NAME}/{destination_path}",
            "file_size_bytes": source.stat().st_size,
        }

    def download(self, source_path: str, destination_path: str) -> dict[str, Any]:
        if not settings.B2_ENABLED:
            raise RuntimeError("Backblaze B2 backups are disabled.")
        raise NotImplementedError("Backblaze B2 download is not implemented yet.")
