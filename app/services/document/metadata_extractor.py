# app/services/document/metadata_extractor.py
"""
Metadata Extractor Service
Phase 3 — Section 4.1
Land Intelligence System
"""

import hashlib
import os
import mimetypes
from typing import BinaryIO, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Optional import for magic bytes detection
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

from app.core.config import settings

# Chunk size for streaming reads (1MB)
CHUNK_SIZE = 1024 * 1024
# Magic bytes header size (first 2KB is enough for MIME detection)
MAGIC_BYTES_SIZE = 2048


class MetadataExtractor:
    """
    Extracts metadata from uploaded documents.
    
    Handles:
    - File size and MIME type detection (using magic bytes)
    - SHA-256 checksum calculation (streaming)
    - PDF page count extraction (lightweight)
    - Basic image metadata (dimensions, format)
    
    Memory-efficient: processes files in chunks, never loads entire file.
    """
    
    def __init__(self):
        """Initialize metadata extractor."""
        pass
    
    async def extract(self, file: BinaryIO, filename: str) -> Dict[str, Any]:
        """
        Extract metadata from a file using streaming reads.
        
        Args:
            file: Binary file stream
            filename: Original filename
            
        Returns:
            Dictionary with extracted metadata
        """
        # Save current position to restore later
        original_pos = file.tell()
        
        try:
            # Move to beginning to read file
            file.seek(0)
            
            # Read magic bytes for MIME detection (first few KB only)
            magic_bytes = file.read(MAGIC_BYTES_SIZE)
            
            # Reset position for checksum calculation
            file.seek(0)
            
            # Calculate checksum and file size via streaming
            checksum, file_size_bytes = await self._calculate_checksum_streaming(file)
            
            # Detect MIME type using magic bytes
            mime_type = self._detect_mime_type(filename, magic_bytes)
            
            # Extract type-specific metadata (from magic bytes only)
            type_metadata = {}
            if mime_type == "application/pdf":
                type_metadata = self._extract_pdf_metadata(magic_bytes)
            elif mime_type.startswith("image/"):
                type_metadata = self._extract_image_metadata(magic_bytes)
            
            # Build metadata dict
            metadata = {
                "file_size_bytes": file_size_bytes,
                "mime_type": mime_type,
                "checksum": checksum,
                "filename": filename,
                "extracted_at": datetime.utcnow().isoformat()
            }
            
            # Add type-specific metadata
            metadata.update(type_metadata)
            
            return metadata
            
        finally:
            # Restore original position
            file.seek(original_pos)
    
    async def _calculate_checksum_streaming(self, file: BinaryIO) -> Tuple[str, int]:
        """
        Calculate SHA-256 checksum and file size using streaming reads.
        
        Args:
            file: Binary file stream
            
        Returns:
            Tuple of (checksum_hex, file_size_bytes)
        """
        sha256_hash = hashlib.sha256()
        file_size = 0
        
        while True:
            chunk = file.read(CHUNK_SIZE)
            if not chunk:
                break
            sha256_hash.update(chunk)
            file_size += len(chunk)
        
        return sha256_hash.hexdigest(), file_size
    
    def _detect_mime_type(self, filename: str, magic_bytes: bytes) -> str:
        """
        Detect MIME type from magic bytes and filename.
        
        Priority:
        1. python-magic (libmagic) if available (most accurate)
        2. Magic byte pattern matching
        3. Filename extension fallback
        
        Args:
            filename: Original filename
            magic_bytes: First 2KB of file content
            
        Returns:
            MIME type string
        """
        # Try python-magic first (most secure)
        if HAS_MAGIC:
            try:
                mime = magic.from_buffer(magic_bytes, mime=True)
                if mime and mime != "application/octet-stream":
                    return mime
            except Exception:
                pass
        
        # Fallback to magic byte detection
        mime = self._detect_mime_from_magic_bytes(magic_bytes)
        if mime:
            return mime
        
        # Final fallback to filename extension
        mime, _ = mimetypes.guess_type(filename)
        if mime:
            return mime
        
        return "application/octet-stream"
    
    def _detect_mime_from_magic_bytes(self, magic_bytes: bytes) -> Optional[str]:
        """
        Detect MIME type from magic bytes.
        
        Args:
            magic_bytes: First few KB of file content
            
        Returns:
            MIME type or None if not detected
        """
        # PDF
        if magic_bytes.startswith(b'%PDF'):
            return "application/pdf"
        
        # JPEG
        if magic_bytes.startswith(b'\xff\xd8\xff'):
            return "image/jpeg"
        
        # PNG
        if magic_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            return "image/png"
        
        # GIF
        if magic_bytes.startswith(b'GIF87a') or magic_bytes.startswith(b'GIF89a'):
            return "image/gif"
        
        # TIFF
        if magic_bytes.startswith(b'II*\x00') or magic_bytes.startswith(b'MM\x00*'):
            return "image/tiff"
        
        # WebP
        if len(magic_bytes) > 12 and magic_bytes[0:4] == b'RIFF' and magic_bytes[8:12] == b'WEBP':
            return "image/webp"
        
        # Microsoft Office (DOC, XLS, PPT - old format)
        if magic_bytes.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
            # Could be DOC, XLS, or PPT
            if b'Word' in magic_bytes or b'Microsoft Word' in magic_bytes:
                return "application/msword"
            if b'Workbook' in magic_bytes:
                return "application/vnd.ms-excel"
            return "application/msword"
        
        # DOCX, XLSX, PPTX (ZIP-based)
        if magic_bytes.startswith(b'PK\x03\x04'):
            # Check for Office Open XML
            if b'word/' in magic_bytes or b'xl/' in magic_bytes or b'ppt/' in magic_bytes:
                if b'word/' in magic_bytes:
                    return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if b'xl/' in magic_bytes:
                    return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                if b'ppt/' in magic_bytes:
                    return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        
        # Plain text (check after binary formats)
        try:
            magic_bytes.decode('utf-8')
            return "text/plain"
        except UnicodeDecodeError:
            pass
        
        return None
    
    def _extract_pdf_metadata(self, magic_bytes: bytes) -> Dict[str, Any]:
        """
        Extract metadata from PDF file header.
        
        Args:
            magic_bytes: First few KB of PDF file
            
        Returns:
            Dictionary with PDF-specific metadata
        """
        metadata = {
            "page_count": 0,
            "is_pdf": True,
            "is_encrypted": False
        }
        
        try:
            # Check for encryption in PDF header
            if b'/Encrypt' in magic_bytes or b'/Standard' in magic_bytes:
                metadata["is_encrypted"] = True
            
            # Count page objects (from header only - may not be complete)
            page_count = magic_bytes.count(b'/Type /Page')
            if page_count == 0:
                page_count = magic_bytes.count(b'/Page ')
            
            # Also check for /Count in Pages dictionary
            import re
            count_match = re.search(rb'/Count\s+(\d+)', magic_bytes)
            if count_match:
                count = int(count_match.group(1))
                if count > page_count:
                    page_count = count
            
            metadata["page_count"] = page_count
            
        except Exception:
            pass
        
        return metadata
    
    def _extract_image_metadata(self, magic_bytes: bytes) -> Dict[str, Any]:
        """
        Extract metadata from image file header.
        
        Args:
            magic_bytes: First few KB of image file
            
        Returns:
            Dictionary with image-specific metadata
        """
        metadata = {
            "is_image": True,
            "image_format": None,
            "width": 0,
            "height": 0
        }
        
        # Detect image format from magic bytes
        if magic_bytes.startswith(b'\xff\xd8\xff'):
            metadata["image_format"] = "jpeg"
        elif magic_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            metadata["image_format"] = "png"
        elif magic_bytes.startswith(b'GIF87a') or magic_bytes.startswith(b'GIF89a'):
            metadata["image_format"] = "gif"
        elif magic_bytes.startswith(b'II*\x00') or magic_bytes.startswith(b'MM\x00*'):
            metadata["image_format"] = "tiff"
        elif len(magic_bytes) > 12 and magic_bytes[0:4] == b'RIFF' and magic_bytes[8:12] == b'WEBP':
            metadata["image_format"] = "webp"
        
        # Extract dimensions
        if metadata["image_format"] == "png":
            # PNG dimensions are at bytes 16-24
            if len(magic_bytes) >= 24:
                width = int.from_bytes(magic_bytes[16:20], byteorder='big')
                height = int.from_bytes(magic_bytes[20:24], byteorder='big')
                metadata["width"] = width
                metadata["height"] = height
                
        elif metadata["image_format"] == "jpeg":
            # Parse JPEG for dimensions
            dimensions = self._parse_jpeg_dimensions(magic_bytes)
            if dimensions:
                metadata["width"], metadata["height"] = dimensions
        
        return metadata
    
    def _parse_jpeg_dimensions(self, content: bytes) -> Optional[Tuple[int, int]]:
        """
        Parse JPEG image dimensions from binary data.
        
        Args:
            content: JPEG file content (first few KB)
            
        Returns:
            Tuple of (width, height) or None if not found
        """
        idx = 0
        length = len(content)
        
        while idx < length - 1:
            if content[idx] != 0xFF:
                idx += 1
                continue
            
            marker = content[idx + 1]
            
            if marker == 0xDA:  # Start of scan
                break
            
            if marker == 0xC0 or marker == 0xC2:  # SOF markers
                if idx + 7 < length:
                    height = int.from_bytes(content[idx + 5:idx + 7], byteorder='big')
                    width = int.from_bytes(content[idx + 7:idx + 9], byteorder='big')
                    return (width, height)
            
            # Skip to next marker
            if idx + 2 < length:
                block_length = int.from_bytes(content[idx + 2:idx + 4], byteorder='big')
                idx += block_length + 2
            else:
                break
        
        return None
    
    async def extract_from_file_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a file on disk.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with extracted metadata, None if file not found
        """
        path = Path(file_path)
        
        if not path.exists():
            return None
        
        with open(path, "rb") as f:
            return await self.extract(f, path.name)
    
    def validate_file_size(self, file_size_bytes: int) -> bool:
        """
        Validate file size against configured maximum.
        
        Args:
            file_size_bytes: File size in bytes
            
        Returns:
            True if within limits, False otherwise
        """
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        return file_size_bytes <= max_bytes
    
    def validate_file_type(self, filename: str) -> bool:
        """
        Validate file extension against allowed extensions.
        
        Args:
            filename: Original filename
            
        Returns:
            True if allowed, False otherwise
        """
        ext = os.path.splitext(filename)[1].lower()
        return ext in settings.ALLOWED_EXTENSIONS