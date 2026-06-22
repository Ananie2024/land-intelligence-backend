# app/utils/path_resolver.py
"""
Path Resolver Utility
Provides safe path resolution to prevent directory traversal vulnerability.
"""

from pathlib import Path
from typing import Union

def resolve_safe_path(base_directory: Union[str, Path], target_path: Union[str, Path]) -> Path:
    """
    Safely resolve a target path relative to a base directory.
    Ensures the resolved path resides strictly within the base directory.
    
    Args:
        base_directory: The root directory that bounds the safe paths.
        target_path: The relative or absolute path to be resolved.
        
    Returns:
        The resolved Path object.
        
    Raises:
        ValueError: If the resolved path is outside the base directory.
    """
    base = Path(base_directory).resolve()
    target = Path(target_path)
    
    # If target path is absolute, resolve it directly. If relative, join with base first.
    if target.is_absolute():
        resolved = target.resolve()
    else:
        resolved = (base / target).resolve()
        
    # Verify the resolved path is within the base directory
    try:
        resolved.relative_to(base)
    except ValueError:
        raise ValueError(
            f"Path security violation: '{target_path}' resolves to '{resolved}', "
            f"which is outside the base storage root '{base}'."
        )
        
    return resolved
