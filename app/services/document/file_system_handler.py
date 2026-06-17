# app/services/document/file_system_handler.py
"""
File System Handler
Phase 3 - Section 4.1
Land Intelligence System
"""

import re
import aiofiles
import os
from pathlib import Path
from typing import BinaryIO, Optional, Any
from uuid import uuid4

from app.core.config import settings


class FileSystemHandler:
    """
    Handles document file storage under the configured storage root.
    Uses asynchronous I/O to prevent blocking the event loop.
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize file storage.

        Args:
            base_path: Optional storage root override
        """
        self.base_path = Path(base_path or settings.FILE_STORAGE_PATH).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        file: Any,  # Can be UploadFile.file or BinaryIO
        filename: str,
        parcel_id: Optional[str] = None,
    ) -> Path:
        """
        Save a file stream asynchronously and return its absolute path.
        """
        target_dir = self._target_directory(parcel_id)
        target_dir.mkdir(parents=True, exist_ok=True)

        safe_name = self._safe_filename(filename)
        target_path = target_dir / f"{uuid4()}_{safe_name}"

        async with aiofiles.open(target_path, "wb") as out_file:
            # If 'file' is already at the end, seek to start
            if hasattr(file, 'seek'):
                file.seek(0)
            
            while True:
                chunk = file.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                await out_file.write(chunk)

        return target_path

    async def get_file(self, file_path: str) -> Any:
        """
        Open a stored file for reading asynchronously.
        """
        path = self._resolve_stored_path(file_path)
        if not path.exists() or not path.is_file():
            return None

        return aiofiles.open(path, "rb")

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a stored file asynchronously if it exists.
        """
        path = self._resolve_stored_path(file_path)
        if not path.exists() or not path.is_file():
            return False

        # os.remove is sync, but small file deletion is usually fast.
        # For high performance, could use aiofiles.os.remove (if available)
        # or run_in_executor.
        os.remove(path)
        return True

    def _target_directory(self, parcel_id: Optional[str]) -> Path:
        if parcel_id:
            return self.base_path / "parcels" / self._safe_path_segment(parcel_id)

        return self.base_path / "unassigned"

    def _resolve_stored_path(self, file_path: str) -> Path:
        path = Path(file_path)
        if not path.is_absolute():
            path = self.base_path / path

        resolved = path.resolve()
        if not self._is_within_base_path(resolved):
            raise ValueError("File path is outside configured storage root")

        return resolved

    def _is_within_base_path(self, path: Path) -> bool:
        try:
            path.relative_to(self.base_path)
            return True
        except ValueError:
            return False

    def _safe_filename(self, filename: str) -> str:
        name = Path(filename).name.strip()
        name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
        return name or "document"

    def _safe_path_segment(self, value: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()) or "unknown"
