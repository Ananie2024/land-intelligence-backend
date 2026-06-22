import logging
import os

logger = logging.getLogger(__name__)


class ManifestValidator:
    def validate(self, file_path: str, expected_checksum: str | None = None) -> bool:
        logger.info("Validating manifest for %s", file_path)
        if expected_checksum is None:
            logger.warning("No checksum provided")
            return False
        if not os.path.exists(file_path):
            logger.warning("File %s not found", file_path)
            return False
        return True
