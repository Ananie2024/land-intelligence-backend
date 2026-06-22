import logging
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.backup.cloud.cloud_storage_interface import CloudStorageInterface

logger = logging.getLogger(__name__)


class GoogleCloudStorageProvider(CloudStorageInterface):
    def upload(self, source_path: str, destination_path: str) -> dict[str, Any]:
        if not settings.GCS_ENABLED:
            raise RuntimeError("Google Cloud Storage backups are disabled.")
        if not settings.GCS_BUCKET_NAME:
            raise RuntimeError("GCS_BUCKET_NAME is required for Google Cloud Storage backups.")

        source = Path(source_path)
        if not source.is_file():
            raise FileNotFoundError(f"Upload source file not found: {source}")

        try:
            from google.cloud import storage
        except ImportError as exc:
            raise RuntimeError("google-cloud-storage is not installed.") from exc

        if settings.GCS_CREDENTIALS_PATH:
            client = storage.Client.from_service_account_json(
                settings.GCS_CREDENTIALS_PATH,
                project=settings.GCS_PROJECT_ID,
            )
        else:
            client = storage.Client(project=settings.GCS_PROJECT_ID)

        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        blob = bucket.blob(destination_path)
        blob.upload_from_filename(str(source))

        logger.info("Uploaded %s to gs://%s/%s", source, settings.GCS_BUCKET_NAME, destination_path)
        return {
            "status": "COMPLETED",
            "destination_path": f"gs://{settings.GCS_BUCKET_NAME}/{destination_path}",
            "file_size_bytes": source.stat().st_size,
        }

    def download(self, source_path: str, destination_path: str) -> dict[str, Any]:
        if not settings.GCS_ENABLED:
            raise RuntimeError("Google Cloud Storage backups are disabled.")
        if not settings.GCS_BUCKET_NAME:
            raise RuntimeError("GCS_BUCKET_NAME is required for Google Cloud Storage backups.")

        try:
            from google.cloud import storage
        except ImportError as exc:
            raise RuntimeError("google-cloud-storage is not installed.") from exc

        if source_path.startswith("gs://"):
            source_path = source_path.split("/", 3)[-1]

        destination = Path(destination_path)
        destination.parent.mkdir(parents=True, exist_ok=True)

        client = storage.Client(project=settings.GCS_PROJECT_ID)
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        bucket.blob(source_path).download_to_filename(str(destination))

        return {
            "status": "COMPLETED",
            "destination_path": str(destination),
            "file_size_bytes": destination.stat().st_size,
        }
