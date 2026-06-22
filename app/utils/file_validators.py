# app/utils/file_validators.py
"""
File Validators Utility
Provides validation logic for file extensions, MIME types, and file sizes.
"""

from typing import List, Set, Union
from pathlib import Path

def validate_file_size(file_size_bytes: int, max_size_mb: float) -> bool:
    """
    Check if the file size is under the specified maximum in Megabytes.
    
    Args:
        file_size_bytes: File size in bytes.
        max_size_mb: Maximum allowed size in Megabytes.
        
    Returns:
        True if the file size is within limits, False otherwise.
    """
    max_bytes = max_size_mb * 1024 * 1024
    return file_size_bytes <= max_bytes

def validate_mime_type(mime_type: str, allowed_types: Union[List[str], Set[str]]) -> bool:
    """
    Check if the MIME type is in the allowed set.
    
    Args:
        mime_type: MIME type of the file.
        allowed_types: List or set of allowed MIME types.
        
    Returns:
        True if allowed, False otherwise.
    """
    return mime_type.lower() in {t.lower() for t in allowed_types}

def is_allowed_extension(filename: str, allowed_extensions: Union[List[str], Set[str]]) -> bool:
    """
    Check if the file extension is allowed.
    
    Args:
        filename: Name or path of the file.
        allowed_extensions: List or set of allowed extensions (e.g., ['.pdf', '.jpg']).
        
    Returns:
        True if allowed, False otherwise.
    """
    ext = Path(filename).suffix.lower()
    normalized_allowed = {e.lower() if e.startswith('.') else f'.{e.lower()}' for e in allowed_extensions}
    return ext in normalized_allowed
