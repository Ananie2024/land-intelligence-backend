"""
Encryption Service for Backup Files
Land Intelligence System

Implements AES-256 encryption for securing backup files before cloud storage.
Uses Fernet (symmetric encryption) from the cryptography library.
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

from cryptography.fernet import Fernet, InvalidToken
import base64

from app.core.config import settings

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Encryption service for securing backup files.
    
    Provides AES-256 symmetric encryption using Fernet for backup file security.
    Supports both in-memory generated keys and persistent key storage.
    """
    
    _key: Optional[bytes] = None
    
    def __init__(self, key_path: Optional[str] = None) -> None:
        """Initialize encryption service with key from config or generate new one."""
        self.key_path: Optional[Path] = None
        if key_path:
            self.key_path = Path(key_path)
        elif hasattr(settings, 'GCS_ENCRYPTION_KEY_PATH'):
            key_path_str = getattr(settings, 'GCS_ENCRYPTION_KEY_PATH', None)
            if key_path_str:
                self.key_path = Path(key_path_str)
        self._load_or_generate_key()
    
    def _load_or_generate_key(self) -> None:
        """Load encryption key from file or generate a new one."""
        if self.key_path and self.key_path.exists():
            try:
                with open(self.key_path, "r", encoding="utf-8") as f:
                    key_data = json.load(f)
                    self._key = base64.urlsafe_b64decode(key_data["key"])
                logger.info("Loaded encryption key from %s", self.key_path)
            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                logger.warning("Failed to load encryption key, generating new one: %s", exc)
                self._generate_key()
        else:
            self._generate_key()
    
    def _generate_key(self) -> None:
        """Generate a new Fernet encryption key."""
        # Fernet.generate_key() creates a URL-safe base64-encoded 256-bit key
        self._key = Fernet.generate_key()
        
        # Save key to file if path is configured
        if self.key_path:
            self.key_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_path, "w", encoding="utf-8") as f:
                json.dump({
                    "key": self._key.decode("utf-8"),
                }, f)
            # Set restrictive permissions (Windows: read-only for owner)
            try:
                os.chmod(self.key_path, 0o600)
            except OSError:
                pass  # Windows may not support Unix permissions
            logger.info("Generated and saved new encryption key to %s", self.key_path)
    
    @property
    def ferkey(self) -> bytes:
        """Get the Fernet key."""
        if self._key is None:
            raise RuntimeError("Encryption key not initialized")
        return self._key
    
    def encrypt(self, file_path: str) -> Dict[str, Any]:
        """
        Encrypt a file for secure backup storage.
        
        Args:
            file_path: Path to the file to encrypt
            
        Returns:
            Dict containing encryption details including:
            - status: "COMPLETED" or "FAILED"
            - encrypted_path: Path to the encrypted file
            - original_size: Original file size in bytes
            - encrypted_size: Encrypted file size in bytes
            - checksum: SHA256 checksum of original file
            
        Raises:
            FileNotFoundError: If the source file doesn't exist
            RuntimeError: If encryption fails
        """
        source_path = Path(file_path).resolve()
        
        if not source_path.exists():
            raise FileNotFoundError(f"File to encrypt not found: {file_path}")
        
        if self._key is None:
            raise RuntimeError("Encryption key not initialized")
        
        try:
            # Calculate original checksum before encryption
            from app.utils.checksum_calculator import calculate_sha256
            original_checksum = calculate_sha256(source_path)
            original_size = source_path.stat().st_size
            
            # Read file contents
            with open(source_path, "rb") as f:
                file_data = f.read()
            
            # Encrypt using Fernet (AES-256 in CBC mode with HMAC)
            fernet = Fernet(self.ferkey)
            encrypted_data = fernet.encrypt(file_data)
            
            # Write encrypted file with .enc extension
            encrypted_path = source_path.with_suffix(source_path.suffix + ".enc")
            with open(encrypted_path, "wb") as f:
                f.write(encrypted_data)
            
            encrypted_size = encrypted_path.stat().st_size
            
            # Store encryption metadata in a sidecar file
            metadata_path = source_path.with_suffix(".encrypt.meta")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump({
                    "original_file": str(source_path.name),
                    "encrypted_file": str(encrypted_path.name),
                    "original_size": original_size,
                    "encrypted_size": encrypted_size,
                    "original_checksum": original_checksum,
                    "encrypted_at": str(os.path.getmtime(encrypted_path)),
                }, f, indent=2)
            
            logger.info(
                "Encrypted %s (%s bytes) -> %s (%s bytes)",
                source_path,
                original_size,
                encrypted_path,
                encrypted_size,
            )
            
            return {
                "status": "COMPLETED",
                "encrypted_path": str(encrypted_path),
                "original_file": str(source_path),
                "original_size": original_size,
                "encrypted_size": encrypted_size,
                "checksum": original_checksum,
                "metadata_path": str(metadata_path),
            }
            
        except Exception as exc:
            logger.error("Encryption failed for %s: %s", file_path, exc, exc_info=True)
            return {
                "status": "FAILED",
                "error_message": str(exc),
            }
    
    def decrypt(self, file_path: str) -> Dict[str, Any]:
        """
        Decrypt an encrypted backup file.
        
        Args:
            file_path: Path to the encrypted file
            
        Returns:
            Dict containing decryption details including:
            - status: "COMPLETED" or "FAILED"
            - decrypted_path: Path to the decrypted file
            - original_checksum: SHA256 checksum for verification
            
        Raises:
            FileNotFoundError: If the encrypted file doesn't exist
            ValueError: If decryption fails or checksum doesn't match
        """
        encrypted_path = Path(file_path).resolve()
        
        if not encrypted_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {file_path}")
        
        if self._key is None:
            raise RuntimeError("Encryption key not initialized")
        
        try:
            # Read encrypted file
            with open(encrypted_path, "rb") as f:
                encrypted_data = f.read()
            
            # Decrypt using Fernet
            fernet = Fernet(self.ferkey)
            try:
                decrypted_data = fernet.decrypt(encrypted_data)
            except InvalidToken as exc:
                raise ValueError("Decryption failed: Invalid key or corrupted file") from exc
            
            # Determine output path (remove .enc extension)
            if encrypted_path.suffix == ".enc":
                decrypted_path = encrypted_path.with_suffix("")
            else:
                decrypted_path = encrypted_path.parent / f"{encrypted_path.name}.decrypted"
            
            # Write decrypted file
            with open(decrypted_path, "wb") as f:
                f.write(decrypted_data)
            
            # Verify checksum if metadata exists
            metadata_path = encrypted_path.parent / f"{encrypted_path.stem}.encrypt.meta"
            original_checksum = None
            if metadata_path.exists():
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    original_checksum = metadata.get("original_checksum")
            
            if original_checksum:
                from app.utils.checksum_calculator import calculate_sha256
                actual_checksum = calculate_sha256(decrypted_path)
                if actual_checksum != original_checksum:
                    logger.warning(
                        "Checksum mismatch for decrypted file %s: expected %s, got %s",
                        decrypted_path,
                        original_checksum,
                        actual_checksum,
                    )
                    # Clean up corrupted file
                    decrypted_path.unlink(missing_ok=True)
                    return {
                        "status": "FAILED",
                        "error_message": "Checksum verification failed - file may be corrupted",
                    }
            
            logger.info("Decrypted %s -> %s", encrypted_path, decrypted_path)
            
            return {
                "status": "COMPLETED",
                "decrypted_path": str(decrypted_path),
                "original_checksum": original_checksum,
                "file_size": decrypted_path.stat().st_size,
            }
            
        except Exception as exc:
            logger.error("Decryption failed for %s: %s", file_path, exc, exc_info=True)
            return {
                "status": "FAILED",
                "error_message": str(exc),
            }

    def get_key_for_backup_manifest(self) -> str:
        """Return the key as a string for storing in backup manifests.
        
        WARNING: Only use this for backup manifest documentation.
        The key itself should be stored securely and separately.
        """
        return self.ferkey.decode("utf-8") if self._key else ""