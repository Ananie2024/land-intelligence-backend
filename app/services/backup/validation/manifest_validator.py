import json
import logging
from pathlib import Path

from app.utils.checksum_calculator import calculate_sha256

logger = logging.getLogger(__name__)


class ManifestValidator:
    def validate(self, file_path: str, expected_checksum: str | None = None) -> bool:
        manifest_path = Path(file_path)
        logger.info("Validating backup manifest %s", manifest_path)

        if not manifest_path.is_file():
            logger.warning("Manifest file %s not found", manifest_path)
            return False

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("Manifest file %s is not valid JSON", manifest_path)
            return False

        archive_path = Path(manifest.get("archive_path", ""))
        manifest_checksum = manifest.get("archive_checksum_sha256")
        if expected_checksum and manifest_checksum != expected_checksum:
            logger.warning("Manifest checksum does not match expected checksum")
            return False

        if not archive_path.is_file():
            logger.warning("Archive listed by manifest does not exist: %s", archive_path)
            return False

        if manifest_checksum and calculate_sha256(archive_path) != manifest_checksum:
            logger.warning("Archive checksum does not match manifest")
            return False

        files = manifest.get("files")
        if not isinstance(files, list):
            logger.warning("Manifest does not contain a files list")
            return False

        return True
