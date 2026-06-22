import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CloudUploadService:
    def upload(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        logger.info("Simulating upload %s -> %s", source_path, destination_path)
        return {"status": "COMPLETED", "source_path": source_path, "destination_path": destination_path}
