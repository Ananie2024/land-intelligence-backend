import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CloudUploadService:
    def upload(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        raise NotImplementedError(
            "Use GoogleCloudStorageProvider or BackblazeB2Provider for real cloud uploads."
        )
