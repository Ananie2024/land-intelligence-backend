import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CloudDownloadService:
    def download(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        raise NotImplementedError(
            "Use a configured cloud provider for real cloud downloads."
        )
