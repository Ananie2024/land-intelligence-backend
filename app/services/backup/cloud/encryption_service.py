import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class EncryptionService:
    def encrypt(self, file_path: str) -> Dict[str, Any]:
        raise NotImplementedError("Backup encryption is not implemented yet.")

    def decrypt(self, file_path: str) -> Dict[str, Any]:
        raise NotImplementedError("Backup decryption is not implemented yet.")
