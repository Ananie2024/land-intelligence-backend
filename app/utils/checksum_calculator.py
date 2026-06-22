# app/utils/checksum_calculator.py
"""
Checksum Calculator Utility
Provides helper functions for calculating cryptographic checksums of files and streams.
"""

import hashlib
from pathlib import Path
from typing import Union, BinaryIO

def calculate_sha256(file_path: Union[str, Path]) -> str:
    """
    Calculate the SHA-256 checksum of a file at the given path.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        Hex-encoded SHA-256 checksum.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(1024 * 1024), b""):  # 1MB chunks
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def calculate_sha256_from_stream(stream: BinaryIO) -> str:
    """
    Calculate the SHA-256 checksum of a binary stream.
    Saves and restores the stream position if seekable.
    
    Args:
        stream: Binary file stream.
        
    Returns:
        Hex-encoded SHA-256 checksum.
    """
    sha256_hash = hashlib.sha256()
    original_pos = 0
    seekable = False
    
    try:
        if hasattr(stream, "seek") and hasattr(stream, "tell"):
            original_pos = stream.tell()
            stream.seek(0)
            seekable = True
    except Exception:
        pass
        
    try:
        for byte_block in iter(lambda: stream.read(1024 * 1024), b""):  # 1MB chunks
            sha256_hash.update(byte_block)
    finally:
        if seekable:
            try:
                stream.seek(original_pos)
            except Exception:
                pass
                
    return sha256_hash.hexdigest()
