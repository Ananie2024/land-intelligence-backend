import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class EncryptionService:
    def encrypt(self, file_path: str) -> Dict[str, Any]:
        logger.info("Simulating encryption for %s", file_path)
        return {"status": "COMPLETED", "encrypted_path": file_path + ".enc"}

    def decrypt(self, file_path: str) -> Dict[str, Any]:
        logger.info("Simulating decryption for %s", file_path)
        return {"status": "COMPLETED", "decrypted_path": file_path.replace(".enc", "")}
